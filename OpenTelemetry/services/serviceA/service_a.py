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

# Set up logging
basicConfig(level=INFO)
logger = getLogger(__name__)

# Set the service name
resource = Resource(attributes={
    "service.name": "serviceA"  # Replace with your actual service name
})

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Configure the OTLP exporter
otlp_exporter = OTLPSpanExporter(endpoint="http://opentelemetry-collector.istio-system.svc.cluster.local:4318/v1/traces")
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

@app.route("/")
def call_service_b():
    with tracer.start_as_current_span("call-service-b") as span:
        trace_id = span.get_span_context().trace_id
        logger.info(f"Calling service B with Trace ID: {trace_id:x}")
        response = get("http://service-b/")
        logger.info(f"Service B responded with Trace ID: {trace_id:x}")
        return "Service B responded with: " + response.text

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
