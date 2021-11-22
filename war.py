# -*- coding: utf8 -*-
import boto3
import argparse
import re
from botocore.config import Config
from botocore.exceptions import ClientError
import logging
import os
import time
import xlsxwriter

#### set options
parser =  argparse.ArgumentParser()
parser.add_argument('--profile')
parser.add_argument('--region')
parser.add_argument('--prefix')
parser.add_argument('--pillar')
parser.add_argument('--milestone', type=int)
parser.add_argument('--output')
parser.add_argument('--outputxls')
parser.add_argument('--s3bucket')
parser.add_argument('--s3key')
parser.add_argument('--s3keyxls')
parser.add_argument('--verbose', action="store_true")
args = parser.parse_args()
profile = args.profile
verbose = args.verbose
output = args.output
outputxls = args.outputxls
bucket = args.s3bucket
key = args.s3key
keyxls = args.s3keyxls

# default output csv file
if output == None:
    output = "war.csv"

try:
    f = open(output, 'w')
except ClientError as e:
    print(output + " cannot be opened - check your output file ")
    logging.error(e)

# defaut output  xlsx file
if outputxls == None:
    outputxls = "war.xlsx"
try:
    workbook = xlsxwriter.Workbook(outputxls)
except ClientError as e:
    print(outputxls + " cannot be opened - check your output xls file ")
    logging.error(e)

worksheet = workbook.add_worksheet('Well Architected Review')
worksheetsummary = workbook.add_worksheet('Notes')

# default region is us-east-1
if args.region == None:
  my_config = Config(
          region_name = 'us-east-1'
          )
else:
  my_config = Config(
          region_name = args.region
          )
if profile == None:
  client = boto3.client('wellarchitected', config=my_config)
  s3_client = boto3.client('s3')
else:
  session = boto3.Session(profile_name=profile)
  client = session.client('wellarchitected', config=my_config)
  s3_client = session.client('s3')

if args.prefix == None:
    prefix=''
else:
    prefix=args.prefix
if args.pillar == None:
    pillars = [ 'security', 'reliability', 'costOptimization', 'operationalExcellence', 'performance' ]
else:
    if args.pillar not in [ 'security', 'reliability', 'costOptimization', 'operationalExcellence', 'performance' ]:
        print("Pillar " + args.pillar + " is not valid" )
        exit(1)
    else:
        pillars = [ args.pillar ]

listworkloads = client.list_workloads(
        WorkloadNamePrefix=prefix
        )

# xlsx worksheets initialization
worksheet.set_column('A:A', 15)
worksheet.set_column('B:B', 9)
worksheet.set_column('C:C', 13)
worksheet.set_column('D:D', 19)
worksheet.set_column('E:E', 75)
worksheet.set_column('F:F', 96)
worksheet.set_column('G:G', 14)
worksheet.set_column('H:H', 26)
worksheet.set_column('I:I', 40)
worksheet.set_column('J:J', 15)
worksheet.set_column('K:K', 75)
title_format = workbook.add_format({'bold': True, 'font_color': '#FFFFFF', 'bg_color': 'purple'})
wrap_format = workbook.add_format({'text_wrap': True})
worksheet.autofilter('A1:K1')

# set header
if verbose == True:
  print("Worload|Milestone|Lens|Pillar|Question Title|Choice Title|Choice Selected|Choice Reason|Choice Reason Notes|Risk|Notes")
f.write("Worload|Milestone|Lens|Pillar|Question Title|Choice Title|Choice Selected|Choice Reason|Choice Reason Notes|Risk|Notes")
f.write('\n')
worksheet.write('A1', 'Workload', title_format)
worksheet.write('B1', 'Milestone', title_format)
worksheet.write('C1', 'Lens', title_format)
worksheet.write('D1', 'Pillar', title_format)
worksheet.write('E1', 'Question Title', title_format)
worksheet.write('F1', 'Choice Title', title_format)
worksheet.write('G1', 'Choice Selected', title_format)
worksheet.write('H1', 'Choice Reason', title_format)
worksheet.write('I1', 'Choice Reason Notes', title_format)
worksheet.write('J1', 'Risk', title_format)
worksheet.write('K1', 'Risk Notes', title_format)

worksheetsummary.set_column('A:A', 15)
worksheetsummary.set_column('B:B', 31)
worksheetsummary.set_column('C:C', 83)
worksheetsummary.set_column('D:D', 14)
worksheetsummary.set_column('E:E', 33)
worksheetsummary.write('A1', 'Workload Name', title_format)
worksheetsummary.write('B1', 'Workload Id', title_format)
worksheetsummary.write('C1', 'Workload ARN', title_format)
worksheetsummary.write('D1', 'Account Owner', title_format)
worksheetsummary.write('E1', 'Last Update', title_format)

## iteration on WARs
l=0
k=0
for id in range(len(listworkloads["WorkloadSummaries"])):
 workloadid=listworkloads["WorkloadSummaries"][id]["WorkloadId"]
 workloadname=listworkloads["WorkloadSummaries"][id]["WorkloadName"]
 workload=client.get_workload(WorkloadId=workloadid)
 if args.milestone == None:
  lenses=client.list_lens_reviews(
        WorkloadId=workloadid
        )
  milestone=''
 else:
  lenses=client.list_lens_reviews(
        WorkloadId=workloadid,
        MilestoneNumber=args.milestone)
  milestone=str(args.milestone)
 k=k+1
 worksheetsummary.write(k, 0, listworkloads["WorkloadSummaries"][id]["WorkloadName"])
 worksheetsummary.write(k, 1, listworkloads["WorkloadSummaries"][id]["WorkloadId"])
 worksheetsummary.write(k, 2, listworkloads["WorkloadSummaries"][id]["WorkloadArn"])
 worksheetsummary.write(k, 3, listworkloads["WorkloadSummaries"][id]["Owner"])
 worksheetsummary.write(k, 4, 'Updated at ' + str(listworkloads["WorkloadSummaries"][id]["UpdatedAt"]))
 # iteration on lenses
 for lensid in range(len(lenses['LensReviewSummaries'])):
   lens=lenses['LensReviewSummaries'][lensid]['LensAlias']
   for pillar in pillars:
    if args.milestone == None:
     answers=client.list_answers(
        WorkloadId=workloadid,
        PillarId=pillar,
        LensAlias=lens,
        MaxResults=20)
    else:
     answers=client.list_answers(
        WorkloadId=workloadid,
        PillarId=pillar,
        LensAlias=lens,
        MilestoneNumber=args.milestone,
        MaxResults=20)
    # iteration on answers
    for i in range(len(answers["AnswerSummaries"])):
     questionid=answers["AnswerSummaries"][i]["QuestionId"]
     if args.milestone == None:
      answer=client.get_answer(
              WorkloadId=workloadid,
              LensAlias=lens,
              QuestionId=questionid
                          )
     else:
      answer=client.get_answer(
              WorkloadId=workloadid,
              LensAlias=lens,
              MilestoneNumber=args.milestone,
              QuestionId=questionid
                          )
     questiontitle=answers["AnswerSummaries"][i]["QuestionTitle"]
     questiontitle=questiontitle.encode('ascii', 'ignore').decode('ascii')
     questiontitle=questiontitle.strip()
     risk_answer=answer["Answer"]["Risk"]
     lenchoiceanswers=len(answer["Answer"]["ChoiceAnswers"])
     # iterations on choices
     for choice in range(len(answer["Answer"]["Choices"])):
      choiceid=answer["Answer"]["Choices"][choice]['ChoiceId']
      choicetitle=answer["Answer"]["Choices"][choice]["Title"]
      choicetitle=choicetitle.encode('ascii', 'ignore').decode('ascii')
      choicetitle=choicetitle.strip().replace("\n", " ")
      choicetitle=re.sub(' +',' ',choicetitle)
      choicetick=""
      choicereason=""
      choicereasonnotes=""
      if answer["Answer"]["Choices"][choice]["ChoiceId"] in answer["Answer"]["SelectedChoices"]:
          choicetick="X"
      for choiceanswer in  range(len(answer["Answer"]["ChoiceAnswers"])):
          if answer["Answer"]["Choices"][choice]["ChoiceId"] == answer["Answer"]["ChoiceAnswers"][choiceanswer]["ChoiceId"]:
               if answer["Answer"]["ChoiceAnswers"][choiceanswer]["Status"] ==  "NOT_APPLICABLE":
                choicetick="NA"
                choicereason=answer["Answer"]["ChoiceAnswers"][choiceanswer]["Reason"]
                choicereasonnotes=answer["Answer"]["ChoiceAnswers"][choiceanswer]["Notes"]
      if verbose == True:
        print(workloadname +  '|' + milestone + '|' + lens + "|" + pillar + "|" + questiontitle + "|" + choicetitle + "|" + choicetick + "|" + choicereason + "|" + choicereasonnotes )
      f.write(workloadname +  '|' + milestone + '|' + lens + "|" + pillar + "|" + questiontitle + "|" + choicetitle + "|" + choicetick + "|" + choicereason + "|" + choicereasonnotes )
      f.write('\n')
      l = l + 1
      worksheet.write(l, 0, workloadname)
      worksheet.write(l, 1, milestone)
      worksheet.write(l, 2, lens)
      worksheet.write(l, 3, pillar)
      worksheet.write(l, 4, questiontitle)
      worksheet.write(l, 5, choicetitle)
      worksheet.write(l, 6, choicetick)
      worksheet.write(l, 7, choicereason)
      worksheet.write(l, 8, choicereasonnotes, wrap_format)

     try:
         notes =  answer["Answer"]["Notes"].replace("\n", " ")
     except:
         notes = ''
     if verbose == True:
       print(workloadname + '|' + milestone + '|' + lens + "|" + pillar + "|" + questiontitle + "|||||" + answer['Answer']['Risk'] + '|' + notes)
     f.write(workloadname + '|' + milestone + '|' + lens + "|" + pillar + "|" + questiontitle + "|||||" + answer['Answer']['Risk'] + '|' + notes)
     f.write('\n')
     l = l + 1
     worksheet.write(l, 0, workloadname)
     worksheet.write(l, 1, milestone)
     worksheet.write(l, 2, lens)
     worksheet.write(l, 3, pillar)
     worksheet.write(l, 4, questiontitle)
     worksheet.write(l, 9, risk_answer)
     worksheet.write(l, 10, notes, wrap_format)
# we close files
f.close()
workbook.close()

print ("Generated WAR csv file in " + output)
print ("Generated WAR xlsx file in " + outputxls)
# copy to S3 bucket if option selected 
if bucket != None:
    if key is None:
        key = os.path.basename(output)
    try:
        s3_response = s3_client.upload_file(output, bucket, key)
    except ClientError as e:
        logging.error(e)
    print("File " + output  + " uploaded to S3 s3://" + bucket + "/" + key)
    if keyxls is None:
        keyxls = os.path.basename(outputxls)
    try:
        s3xls_response = s3_client.upload_file(outputxls, bucket, keyxls)
    except ClientError as e:
        logging.error(e)
    print("File " + outputxls  + " uploaded to S3 s3://" + bucket + "/" + keyxls)
