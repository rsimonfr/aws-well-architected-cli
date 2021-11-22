# well-architected-review

This repo intends to publish some scripts related to Well Architected Reviews.
war.py extracts in txt & xlsx files all the WAR that exists in the account and the specified region.
It works when launched from AWS CloudShell &  with an AWS Cli

The script requires you use a profile which has access to Well Architected Tool Reviews at least in reading
If you are using --s3bucket option it will require write access to target bucket

Before launching the script, insure you have very latest version of AWS Boto3 SDK & Python 3  & xlsxwriter:

   pip3 install -r requirements.txt

To launch the script:

python3 war.py

Available options:

  --output specify output csv file : if not set generates a war.csv file in current directory

  --outputxls specify output xlsx file : if not set generates a war.xlsx file in current directory

  --pillar to extract only one pillar
    valid values are :  'security', 'reliability', 'costOptimization', 'operationalExcellence', 'performance'  
    
  --prefix to extract WAR with  a specific description prefix

  --milestone to extract specific milestone id for a WAR

  --s3bucket where to copy WAR file to S3

  --s3key optional if s3bucket is set: if not set take the name of local csv file  as target.

  --s3keyxls optional if s3bucket is set: if not set take the name of local xlsx file as target.

  --verbose (no option) to print the lines to the screen

  --profile to specify a specific profile of your AWS  client - if not set takes the default  

  --region to specify the region where the WAR was done - if not set will check on us-east-1 region (North Virginia)

The war.py script uses | as delimiter as usual , delimiter in csv may be in the notes.
It has been tested on wellarchitected and serverless lens and tries to avoid all strange characters in the questions and choices but should work on others

it comes with an header and have following fields

Worload|Milestone|Lens|Pillar|Question Title|Choice Title|Choice Selected|Risk|Notes

Risk & Notes appear in the last line for each question. If there were line feeds in the notes they are deleted.
An X is put in Choice Selected if the choice has been selected
