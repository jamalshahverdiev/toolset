from flask import Flask
from requests import get
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from logging import basicConfig, INFO, getLogger

basicConfig(level=INFO)
logger = getLogger(__name__)

resource = Resource(attributes={
    "service.name": "serviceB"  
})

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()  

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="http://opentelemetry-collector.istio-system.svc.cluster.local:4318/v1/traces")
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

@app.route("/")
def home():
    with tracer.start_as_current_span("call-service-c") as span:
        trace_id = span.get_span_context().trace_id
        logger.info(f"Calling service C with Trace ID: {trace_id:x}")
        response = get("http://service-c/")
        logger.info(f"Service C responded with Trace ID: {trace_id:x}")
        return "Service C responded with: " + response.text
    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
