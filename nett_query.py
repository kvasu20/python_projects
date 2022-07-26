#!/usr/bin/env python3

import sys
import json
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import itertools
import readline
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

swagger_api_url = "https://X.X.X.X/netTerrain/wapi/v1/"

def get_response_body(endpoint):
    #print("in get resp body")
    response = requests.get(endpoint, auth = ('username', 'password'), verify=False)
    #print(response)
    response_body_txt = json.loads(response.text)  ##this is a dict 
    #print(response_body_txt)
    return response_body_txt

def get_ip_address():
    #print("in get ip addr")
    print("\n")
    ip_addr = input("Enter IP address of the switch:")
    return ip_addr

def ip_address_check(ip_addr):
    #print("in ip addr check")
    #node_prop_value_endpoint = "https://X.X.X.X/netTerrain/wapi/v1/nodes?node_property_values.value="
    node_prop_value_endpoint = swagger_api_url + "nodes?node_property_values.value="
    #print(node_prop_value_endpoint)
    node_endpoint_full = node_prop_value_endpoint + ip_addr
    #print(node_endpoint_full)
    node_endpoint_full_resp = get_response_body(node_endpoint_full)
    resp_total_items = node_endpoint_full_resp["total_items"]
    #print(f"Resp_total_items = {resp_total_items}")
    if resp_total_items == 0:
        print("\n")
        print(f"No entry found for IP address {ip_addr}")
        print("\n")
        quit()
    else:
        print("\n")
        print(f"Entry found for IP {ip_addr}")
        print("\n")
        resp_items_list = node_endpoint_full_resp["_items"]    
        #print(resp_items_list)
        return resp_items_list

def get_intf_num():
    #print("in get intf num")
    print("Enter the interface (access port) number. Ex: Enter '1/0/1' if the interface is Gi1/0/1")
    print("\n")
    stack_intf = input("Interface Number:")
    print("\n")
    stack_intf_splitted = stack_intf.split("/")
    if int(stack_intf_splitted[1]) > 0:
        print("\n")
        print("Invalid interface. Enter correct access port number.")
        print("\n")
        quit()
    switch_stack_num = stack_intf_splitted[0]
    switch_stack_num = int(switch_stack_num)
    #print(f"switch_stack_num : {switch_stack_num}")
    intf_num = stack_intf_splitted[-1]
    #print(f"intf_num : {intf_num}")
    return switch_stack_num, intf_num

##arg is a list of endpoints
def get_ip_match_nodes_ids(nodes_endpoints_list):
    #print("in get_ip_match_nodes_ids")
    #print(nodes_endpoints_list)
    node_id_list = []
    for i in range(len(nodes_endpoints_list)):
        endpoint = nodes_endpoints_list[i]["href"]
        #print("\n")
        splitted = endpoint.split("/")
        #print("\n")
        node_id_list.append(splitted[-1])
    return node_id_list

def get_match_port_endpoint(node_id_list, switch_stack_num, interf_num):
    #print("In get_match_port_endpoint")
    node_id = node_id_list[switch_stack_num - 1]
    #print(f"node_id: {node_id}")
    port_search_endpoint = swagger_api_url + "devices/" + node_id + "/ports?Name=" + interf_num
    #print(f"port_search_endpoint: {port_search_endpoint}")
    port_search_resp = get_response_body(port_search_endpoint) ##this is dict  
    #print(f"port_search_resp: {port_search_resp}")
    match_port_endpoint = get_items_list_href_value(port_search_resp, 0)
    #print(f"match_port_endpoint: {match_port_endpoint}")
    return match_port_endpoint

def get_dict_value(resp_dict, key):
    value = resp_dict[key]
    return value   ###this is a string or a list in case of key = "_items"

def get_href_value(resp_dict):
    href_value = resp_dict["href"]
    return href_value

def get_list_element(item_list, list_index):
    element = item_list[list_index]
    return element

def get_items_list_href_value(resp_dict, list_index = 0):
    resp_items_list = get_dict_value(resp_dict,"_items")
    if len(resp_items_list)  == 0:
        return 0
    else:
        href_value = resp_items_list[list_index]["href"]
        return href_value


def main():
    node_id_list = get_ip_match_nodes_ids(ip_address_check(get_ip_address()))
    #print(f"node_id_list: {node_id_list}")
    switch_stack_num, interf_num = get_intf_num()
    #print(f"switch_stack_num : {switch_stack_num}")
    #print(f"interf_num : {interf_num}")
    
    switch_link_endpoint = get_items_list_href_value(get_response_body(get_match_port_endpoint(node_id_list, switch_stack_num, interf_num) + "/links"))
    #print(f"switch_link_endpoint : {switch_link_endpoint}")
    if switch_link_endpoint == 0:
        print("Switch port not patched to the panel!")
        print("\n")
        quit()

    front_panel_port_endpoint = get_dict_value(get_dict_value(get_response_body(switch_link_endpoint), "to_node"), "href")
    #print(f"front_panel_port_endpoint: {front_panel_port_endpoint}")

    switch_port_endpoint = get_dict_value(get_dict_value(get_response_body(switch_link_endpoint), "from_node"), "href")
    #print(f"switch_port_endpoint: {switch_port_endpoint}")
    
    front_panel_port_links_endpoint = front_panel_port_endpoint + "/links"
    front_panel_port_links_endpoint_items_list = get_response_body(front_panel_port_links_endpoint)["_items"]
    #print(f"front_panel_port_links_endpoint_items_list : {front_panel_port_links_endpoint_items_list}")

    switch_port_link_endpoint = switch_port_endpoint + "/links"
    switch_port_link_endpoint_items_list = get_response_body(switch_port_link_endpoint)["_items"]
    #print(f"switch_port_link_endpoint_items_list : {switch_port_link_endpoint_items_list}")

    panel_front_to_back_link_endpoint_list =  list(itertools.filterfalse(lambda x: x in front_panel_port_links_endpoint_items_list, switch_port_link_endpoint_items_list)) + list(itertools.filterfalse(lambda x: x in switch_port_link_endpoint_items_list, front_panel_port_links_endpoint_items_list))
    #print(f"panel_front_to_back_link_endpoint_list: {panel_front_to_back_link_endpoint_list}")

    panel_front_to_back_link_endpoint_resp = get_response_body(get_href_value(get_list_element(panel_front_to_back_link_endpoint_list, 0)))
    #print(f"panel_front_to_back_link_endpoint_resp : {panel_front_to_back_link_endpoint_resp}")
    back_panel_port_endpoint = get_dict_value(get_dict_value(panel_front_to_back_link_endpoint_resp, "to_node"), "href")
    #print(f"back_panel_port_endpoint : {back_panel_port_endpoint}")
    back_panel_port_links_endpoint_items_list = get_response_body(back_panel_port_endpoint + "/links")["_items"]
    #print(f"back_panel_port_links_endpoint_items_list : {back_panel_port_links_endpoint_items_list}")

    panel_back_to_wall_link_endpoint_list = list(itertools.filterfalse(lambda x: x in panel_front_to_back_link_endpoint_list, back_panel_port_links_endpoint_items_list)) + list(itertools.filterfalse(lambda x: x in back_panel_port_links_endpoint_items_list, panel_front_to_back_link_endpoint_list))
    #print(f"panel_back_to_wall_link_endpoint_list : {panel_back_to_wall_link_endpoint_list}")
    
    if len(panel_back_to_wall_link_endpoint_list) == 0:
        print("\n")
        print("Wall Jack not patched to the panel!")
        print("\n")
        quit()
    else:
        panel_back_to_wall_link_endpoint_resp = get_response_body(get_href_value(get_list_element(panel_back_to_wall_link_endpoint_list, 0)))
        #print(f"panel_back_to_wall_link_endpoint_resp : {panel_back_to_wall_link_endpoint_resp}")
        wall_jack_endpoint = get_dict_value(get_dict_value(panel_back_to_wall_link_endpoint_resp, "from_node"), "href")
        #print(f"wall_jack_endpoint : {wall_jack_endpoint}")
        wall_jack_endpoint_resp = get_response_body(get_dict_value(get_dict_value(panel_back_to_wall_link_endpoint_resp, "from_node"), "href"))
        #print(f"wall_jack_endpoint_resp : {wall_jack_endpoint_resp}")
        wall_jack_ID = get_dict_value(wall_jack_endpoint_resp, "name")
        #print(f"wall_jack_ID : {wall_jack_ID}")
        wall_jack_breadcrumbs = get_dict_value(wall_jack_endpoint_resp, "breadcrumbs").replace("Top Level>","") 
        #print(f"wall_jack_breadcrumbs : {wall_jack_breadcrumbs}")

        wall_jack_prop_endpoint = get_dict_value(get_dict_value(wall_jack_endpoint_resp, "node_property_values"), "href")
        #print(f"wall_jack_prop_endpoint : {wall_jack_prop_endpoint}")
        wall_jack_prop_endpoint_resp = get_response_body(get_dict_value(get_dict_value(wall_jack_endpoint_resp, "node_property_values"), "href"))
        #print(f"wall_jack_prop_endpoint_resp :{wall_jack_prop_endpoint_resp}") 
        
        room_num = get_dict_value((get_response_body(get_dict_value((get_list_element((get_dict_value(wall_jack_prop_endpoint_resp, "_items")),2)), "href"))), "value")
        #print(f"room_num : {room_num}")
        
        wall_jack_loc = wall_jack_breadcrumbs + ">" + room_num + ">" + wall_jack_ID
        print(f"Wall Jack location: {wall_jack_loc}")
        print("\n")


if __name__ == "__main__":
    main()


