NAME=aft-lambda
CREATE_LAMBDA=1
HANDLER=lambda_function.lambda_handler
while getopts cn:h: flag
do
    case "${flag}" in
        c) CREATE_LAMBDA=0;;
        n) NAME=${OPTARG};;
        h) HANDLER=${OPTARG};;
    esac
done
rm -f *.zip
zip -r $NAME.zip . -x aft_test/\*
aws s3 cp $NAME.zip s3://tasc-lambdas
if [ $CREATE_LAMBDA == 0 ]
    then aws lambda create-function --function-name $NAME --runtime python3.7 --role arn:aws:iam::861473675836:role/TASCLambda --handler ${HANDLER} --timeout 120 --memory-size 2048 --code S3Bucket=tasc-lambdas,S3Key=${NAME}.zip
else
    aws lambda update-function-code --s3-bucket "tasc-lambdas" --s3-key "${NAME}.zip" --function-name $NAME
fi 
