#!/usr/bin/env python
# coding=utf-8

import datetime
import gitlab
import collections
import pandas as pd

# ouR-GWJzqDUD7NBUPHWb
gl = gitlab.Gitlab(url='http://192.168.2.182:9000/', private_token='o4r9GFrKRexTkZbcrznk', timeout=60)

projectn = {}

# 查所有项目id

for i in gl.projects.list(all=True, as_list=False):
    name = str(i.name)+'蒋康'
    id = str(i.id)
    projectn.update({i.name: i.id})
    projecta = pd.DataFrame(list(projectn.items()))
    projecta.columns = ['project', 'id']
    #
    # with open(r'C:\Users\DELL\Desktop\孔繁阳\git统计\Users.txt', 'a') as f:
    #     f.write(name+'\t'+id+'\n')


projecta.to_excel(r'C:\Users\DELL\Desktop\孔繁阳\git统计\项目list.xlsx')

# 读取固定项目列表
projectb = pd.read_excel(r'C:\Users\DELL\Desktop\孔繁阳\git统计\项目id.xlsx')


projectc = pd.merge(projectb, projecta, on='project', how='left')
dlist = projectc['id'].to_list()



# 固定分支
# elist = ['master', 'b_pre', 'b_test_01', 'b_test_02']

elist = ['master']


# 开始结束时间
start_time = '2022-05-01T00:00:00Z'
end_time = '2022-05-31T23:59:59Z'

# 获取数据


def get_gitlab():
    """
    gitlab API
    """
    list2 = []
    projects = gl.projects.list(all=True)
    # print(projects)
    # project = gl.projects.get(234)

    # print(project.branches.list())
    # branches = project.branches.list()
    # branch = project.branches.get('master')
    # print(branch)

    num = 0
    for i in range(len(dlist)):
        num += 1
        project = gl.projects.get(dlist[i])
        print("查看了%d个项目" % num)
        for f in range(len(elist)):
            commits = project.commits.list(all=True, query_parameters={'since': start_time, 'until': end_time,
                                                                       'ref_name': elist[f]})

            if len(commits) == 0:
                print('项目：{0}  分支：{1}为空'.format(project.name, elist[f]))


            for commit in commits:
                com = project.commits.get(commit.id)

                pro = {}
                try:
                    # print(project.path_with_namespace,com.author_name,com.stats["total"])
                    pro["projectName"] = project.path_with_namespace
                    pro["authorName"] = com.author_name
                    pro["branch"] = elist[f]
                    pro["additions"] = com.stats["additions"]
                    pro["deletions"] = com.stats["deletions"]
                    pro["commitNum"] = com.stats["total"]
                    list2.append(pro)
                except:
                    print("error")

    return list2


# 统计数据


def data():
    """
    数据去重
    key split
    """

    ret = {}

    for ele in get_gitlab():
        key = ele["projectName"] + ele["authorName"] + ele["branch"]
        if key not in ret:
            ret[key] = ele
            ret[key]["commitTotal"] = 1
        else:
            ret[key]["additions"] += ele["additions"]
            ret[key]["deletions"] += ele["deletions"]
            ret[key]["commitNum"] += ele["commitNum"]
            ret[key]["commitTotal"] += 1

    list1 = []
    for key, v in ret.items():
        v["项目名"] = v.pop("projectName")
        v["开发者"] = v.pop("authorName")
        v["分支"] = v.pop("branch")
        v["添加代码行数"] = v.pop("additions")
        v["删除代码行数"] = v.pop("deletions")
        v["提交总行数"] = v.pop("commitNum")
        v["提交次数"] = v["commitTotal"]
        list1.append(v)
    return list1


# 导出Excel

def excel(excelName):
    """
    excel
    """
    writer = pd.ExcelWriter(excelName)
    df = pd.DataFrame(data(), columns=["项目名", "开发者", "分支", "添加代码行数", "删除代码行数", "提交总行数", "提交次数"])
    df['实际行数'] = df['添加代码行数'] - df['删除代码行数']
    df.to_excel(writer, sheet_name='按人员统计', index=None)
    dft = df.groupby('项目名')['实际行数'].sum().reset_index()
    dft.to_excel(writer, sheet_name='按项目统计', index=None)
    writer.save()


if __name__ == "__main__":
    excel(r'C:\Users\DELL\Desktop\孔繁阳\git统计\gitlab.xlsx')
