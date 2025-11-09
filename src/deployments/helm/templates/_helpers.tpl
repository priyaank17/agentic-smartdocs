{{- define "smartdocs-agentic.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name -}}
{{- end -}}

{{- define "smartdocs-agentic.labels" -}}
helm.sh/chart: {{ include "smartdocs-agentic.fullname" . }}
app.kubernetes.io/managed-by: Helm
{{- end -}}

{{- define "smartdocs-agentic.selectorLabels" -}}
app.kubernetes.io/name: {{ include "smartdocs-agentic.fullname" . }}
{{- end -}}
