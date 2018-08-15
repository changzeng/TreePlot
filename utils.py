# encoding: utf-8

import json, copy

# 小数点后的保留位数
reserve_bit = 4

def get_div(a, b):
    if b == 0:
        return 0.0
    return round(a*1.0/b, reserve_bit)

def make_node(name="", parent="null"):
    return {"name": name,  "parent": parent,  "children": []}

def make_value(name, value, aggreation_type, parameter_a="", parameter_b=""):
    return {"name": name, "value": value, "aggreation_type": aggreation_type, "parameter_a": parameter_a, "parameter_b": parameter_b}

def pre_process(file_name):
    result = {}
    with open(file_name) as fd:
        _dict = json.load(fd)
    total_cvt_num = 0
    total_person_num = 0
    for key, values in _dict.items():
        total_cvt_num += values[0]
        total_person_num += values[1]
    for key, values in _dict.items():
        cvt_num = values[0]
        person_num = values[1]
        result[key] = []
        result[key].append(make_value(u"转化人数", cvt_num, "sum"))
        result[key].append(make_value(u"人数", person_num, "sum"))
        result[key].append(make_value(u"总转化人数", total_cvt_num, "steady"))
        result[key].append(make_value(u"总人数", total_person_num, "steady"))
        result[key].append(make_value(u"转化率", get_div(cvt_num, person_num), "div", u"转化人数", u"人数"))
        result[key].append(make_value(u"人数占比", get_div(person_num, total_person_num), "div", u"人数", u"总人数"))
        result[key].append(make_value(u"转化占比", get_div(cvt_num, total_cvt_num), "div", u"转化人数", u"总转化人数"))
    return result

def convert_to_json(file_name):
    # preprocess
    _dict = pre_process(file_name)
    # build tree
    root = make_node(parent="null")
    def is_children(key, node):
        for child in node["children"]:
            if key == child["name"]:
                return child
        return None
    for key, values in _dict.items():
        fields = key.split("-")
        pre = root
        for field in fields:
            child = is_children(field, pre)
            if child is not None:
                pre = child
            else:
                cur = make_node(name=field, parent=pre["name"])
                pre["children"].append(cur)
                pre = cur
        pre["values"] = values
    # aggreation tree
    def get_value(values, name):
        for value_dic in values:
            if value_dic["name"] == name:
                return value_dic["value"]
        return None
    def dfs(node):
        if len(node["children"]) != 0:
            values = []
            for child_index, child in enumerate(node["children"]):
                dfs(child)
                for value_index, value_dic in enumerate(child["values"]):
                    if child_index == 0:
                        values.append(copy.deepcopy(value_dic))
                        continue
                    if value_dic["aggreation_type"] == "sum":
                        values[value_index]["value"] += value_dic["value"]
            for value_index, value_dic in enumerate(values):
                if value_dic["aggreation_type"] == "div":
                    a = value_dic["parameter_a"]
                    b = value_dic["parameter_b"]
                    a = get_value(values, a)
                    b = get_value(values, b)
                    value_dic["value"] = get_div(a, b)
            node["values"] = values
        values = node["values"]
        tmp = ""
        line_breaker = "\n"
        for value_index, value_dic in enumerate(values):
            tmp += value_dic["name"]+":"
            if type(value_dic["value"]) == float:
                tmp += "{0:.6}%".format(round(value_dic["value"], reserve_bit)*100)
            else:
                tmp += str(value_dic["value"])
            if value_index+1 != len(values):
                tmp += line_breaker
        node["name"] += line_breaker + tmp
        node["children"] = sorted(node["children"], key=lambda x:x["name"])
    dfs(root)

    return root["children"][0]
