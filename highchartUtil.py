# -*- coding: utf-8 -*-
import sys,os
import json
def genChartJson(jsonFileName,groupname,day,unrunedModuleList,failReportList,moduleDict):
    modules=[]
    failCases=[]
    totalCases=[]
    headerList=failReportList[0].keys()
    for failReport in failReportList:
        moduleId=failReport["module_id"]
        moduleName=moduleDict[moduleId]
        modules.append(moduleName)
        failCase=int(failReport["failure_case"])
        failCases.append({"y":failCase})
        totalCase=int(failReport["total_case"])
        totalCases.append({"y":totalCase})
    for moduleName in unrunedModuleList:
        modules.append(moduleName)
        failCases.append({"y":0})
        totalCases.append({"y":0})
    highdata={
        "chart": {
            "type": 'column'
        },
        "title": {
            "text": u'TEST %s ENVIRONMENT %s CASE STATISTIC' % (groupname,day)
        },
        "subtitle": {
            "text": 'Source: '
        },
        "xAxis": {
            "categories":modules
        },
        "yAxis": {
            "min": 0,
            "title": {
                "text": u'FAILED NUMBER'
            }
        },
        "tooltip": {
            "headerFormat": '<span style="font-size:10px">{point.key}</span><table>',
            "pointFormat":  '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                u'<td style="padding:0"><b>{point.y} NUMBER</b></td></tr>',
            "footerFormat": '</table>',
            "shared":  True,
            "useHTML": True
        },
        "plotOptions": {
            "column": {
                "pointPadding": 0.2,
                "borderWidth": 0
            }
        },
        "series": [{
            "name":u'FAILED TESTING REGRESSION',
            "data": failCases,
            "dataLabels": {
                "enabled": True
            }
        }]
    }
    print(highdata)
    strhighdata=json.dumps(highdata)
    open(jsonFileName,"w").write(strhighdata)

