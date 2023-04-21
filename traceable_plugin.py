import agent_util
import requests

from prometheus_client.parser import text_string_to_metric_families


class TraceablePlugin(agent_util.Plugin):
    textkey = "traceable_plugin"
    label = "Traceable Platform Agent Monitor"

    @classmethod
    def get_metadata(self, config):

        status = agent_util.SUPPORTED
        msg = None

        metric_response = requests.get("http://localhost:8888/metrics")
        if metric_response.status_code != 200:
            status = agent_util.MISCONFIGURED
            msg = "Metric Endpoint Not reachable"

        metadata = {
            "otelcol_exporter_sent_spans_total": {
                "label": "otelcol_exporter_sent_spans_total",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "number"
            },
            "otelcol_exporter_sent_metric_points_total": {
                "label": "otelcol_exporter_sent_metric_points_total",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "number"
            },
            "otelcol_exporter_enqueue_failed_spans_total": {
                "label": "otelcol_exporter_enqueue_failed_spans_total",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "number"
            },
            "otelcol_exporter_enqueue_failed_metric_points_total": {
                "label": "otelcol_exporter_enqueue_failed_metric_points_total",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "unit description"
            },
            "otelcol_exporter_send_failed_spans_total": {
                "label": "otelcol_exporter_send_failed_spans_total",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "unit description"
            },
            "otelcol_exporter_send_failed_metric_points_total": {
                "label": "otelcol_exporter_send_failed_metric_points_total",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "unit description"
            }
        }
        return metadata

    def check(self, textkey, data, config):
        metric_response = requests.get("http://localhost:8888/metrics")
        if metric_response.status_code != 200:
            return 0

        metric_response_text = metric_response.text

        for family in text_string_to_metric_families(metric_response_text):
            for sample in family.samples:
                name = sample.name
                value = sample.value

                if textkey == name:
                    cached_results = self.get_cache_results(textkey, data)
                    self.cache_result(textkey, data, value)

                    # If this is the first data point we won't return it
                    # As the values are cumulative we need to calculate the
                    # diff between the last value and the current value
                    new_value = 0
                    if cached_results != None and len(cached_results) > 0:
                        _, old_value = cached_results[0]
                        new_value = value - old_value

                    return new_value
        return 0


""" if __name__ == "__main__":
    metric_response = requests.get("http://localhost:8888/metrics")

    metric_response_text = metric_response.text
    print(metric_response_text, " ", metric_response.status_code)

    for family in text_string_to_metric_families(metric_response_text):
        for sample in family.samples:
            name = sample.name
            value = sample.value
            # if name == "otelcol_exporter_sent_spans_total":
            print("Name: {0} Labels: {1} Value: {2}".format(*sample))
    ret = []
    ret.append((1, 2))
    ret.append((3, 4))
    print(str(ret))
    for a, b in ret:
        print(str(a), ' ', str(b))
    print(str(len(ret)))
 """
