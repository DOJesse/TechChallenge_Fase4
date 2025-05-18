FROM grafana/grafana:latest

# Provisioning de data sources e dashboards
COPY provisioning /etc/grafana/provisioning

# Dashboards JSON
COPY dashboards /var/lib/grafana/dashboards

# Provisioning datasource (opcional, se você já tem)
# COPY provisioning/datasource.yaml /etc/grafana/provisioning/datasources/
