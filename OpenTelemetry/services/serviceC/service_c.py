from flask import Flask
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from logging import basicConfig, INFO, getLogger

# Set up logging
basicConfig(level=INFO)
logger = getLogger(__name__)

# Set the service name
resource = Resource(attributes={
    "service.name": "serviceC"
})

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="http://opentelemetry-collector.istio-system.svc.cluster.local:4318/v1/traces")
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

@app.route("/")
def home():
    current_span = trace.get_current_span()
    trace_id = current_span.get_span_context().trace_id
    logger.info(f"Service C received request with Trace ID: {trace_id:x}")
    return "Hello from Service C"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5002)
