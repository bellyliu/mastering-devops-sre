# Logout of helm registry to perform an unauthenticated pull against the public ECR
helm registry logout public.ecr.aws

KARPENTER_VERSION="1.8.3"
CLUSTER_NAME="ashutosh-eks"
KARPENTER_NAMESPACE="karpenter"


helm upgrade --install karpenter oci://public.ecr.aws/karpenter/karpenter --version "${KARPENTER_VERSION}" --namespace "${KARPENTER_NAMESPACE}" --create-namespace \
  --set "settings.clusterName=${CLUSTER_NAME}" \
  --set "settings.interruptionQueue=${CLUSTER_NAME}" \
  --set settings.featureGates.spotToSpotConsolidation=true \
  --set controller.resources.requests.cpu=1 \
  --set controller.resources.requests.memory=1Gi \
  --set controller.resources.limits.cpu=1 \
  --set controller.resources.limits.memory=1Gi \
  --wait
