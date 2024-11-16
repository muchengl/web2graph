# Function to fetch EC2 instance public DNS by name
get_ec2_dns() {
  # Check if an instance name was provided
  if [ -z "$1" ]; then
    echo "Usage: Please provide the EC2 instance name."
    return 1
  fi

  INSTANCE_NAME=$1

  # Get the instance ID of the specified EC2 instance by its name
  INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=$INSTANCE_NAME" \
    --query "Reservations[*].Instances[*].InstanceId" \
    --output text)

  # Check if the instance was found
  if [ -z "$INSTANCE_ID" ]; then
    echo "No instance found with the name '$INSTANCE_NAME'."
    return 1
  fi

  # Fetch the public DNS name of the specified instance
  PUBLIC_DNS=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query "Reservations[*].Instances[*].PublicDnsName" \
    --output text)

  # Output the DNS name
  echo "$PUBLIC_DNS"
}


#source ./aws/aws-cli.sh
export WEBARENA_HOST=$(get_ec2_dns "WebArenaEc2Stack/WebArenaServer")
echo "WebArena Host: $WEBARENA_HOST"

HOSTNAME=$WEBARENA_HOST

echo export WEBARENA_HOST=$WEBARENA_HOST
echo export DATASET=visualwebarena

echo export CLASSIFIEDS="http://$HOSTNAME:9980"
echo export CLASSIFIEDS_RESET_TOKEN="4b61655535e7ed388f0d40a93600254c"  # Default reset token for classifieds site, change if you edited its docker-compose.yml
echo export SHOPPING="http://$HOSTNAME:7770"
echo export REDDIT="http://$HOSTNAME:9999"
echo export WIKIPEDIA="http://$HOSTNAME:8888"
echo export HOMEPAGE="http://$HOSTNAME:4399"

echo export SHOPPING_ADMIN="http://$HOSTNAME:7780/admin"
echo export GITLAB="http://$HOSTNAME:8023"
echo export MAP="http://$HOSTNAME:3000"



# Uncommented examples:
# echo export WEBARENA_HOST=$WEBARENA_HOST
# echo export SHOPPING="http://$HOSTNAME:7770"
# echo export SHOPPING_ADMIN="http://$HOSTNAME:7780/admin"
# echo export REDDIT="http://$HOSTNAME:9999"
# echo export GITLAB="http://$HOSTNAME:8023"
# echo export MAP="http://$HOSTNAME:3000"
# echo export WIKIPEDIA="http://$HOSTNAME:8888/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"
# echo export HOMEPAGE="http://$HOSTNAME:4399"
