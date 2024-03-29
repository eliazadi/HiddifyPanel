from flask import g
import enum
from hiddifypanel.models import User,Domain,BoolConfig,StrConfig,DomainType,ConfigEnum,get_hconfigs,get_hdomains,hconfig,Proxy
import yaml
from hiddifypanel.panel import hiddify
def all_proxies():
    all_proxies=hiddify.get_available_proxies()
    all_proxies=[p for p in all_proxies if p.enable]
    # all_cfg=Proxy.query.filter(Proxy.enable==True).all()
    # if not hconfig(ConfigEnum.domain_fronting_domain):
    #     all_cfg=[c for c in all_cfg if 'Fake' not in c.cdn]
    # if not g.is_cdn:
    #     all_cfg=[c for c in all_cfg if 'CDN' not in c.cdn]
    # if not hconfig(ConfigEnum.ssfaketls_enable):
    #     all_cfg=[c for c in all_cfg if 'faketls' not in c.transport and 'v2ray' not in c.proto]
    # if not hconfig(ConfigEnum.vmess_enable):
    #     all_cfg=[c for c in all_cfg if 'vmess' not in c.proto]

     
    return all_proxies

def proxy_info(name, mode="tls"):
    return "error"

def pbase64(full_str):
    return full_str
    str=full_str.split("vmess://")[1]
    import base64
    resp=base64.b64encode(f'{str}'.encode("utf-8"))
    return "vmess://"+resp.decode()



def make_proxy(proxy):
    l3=proxy.l3

    domain = g.domain
    hconfigs=get_hconfigs()
    port=0
    if l3 in ["tls"]:
        port=443
    elif l3 =="http":
        port = 80
    elif l3 =="kcp":
        port = hconfig(ConfigEnum.kcp_ports).split(",")[0]
    elif l3 =="tuic":
        port = hconfig(ConfigEnum.tuic_port).split(",")[0]
    
    name=proxy.name   
    is_cdn="CDN" in name
    direct_host=domain if is_cdn else g.direct_host
    
    base={
        'name':name.replace(" ", "_"),
        'cdn':is_cdn,
        'mode':"CDN" if is_cdn else "direct",
        'l3': l3,
        'port': port,
        'server':domain if is_cdn else g.direct_host,
        'sni':domain,
        'uuid':str(g.user_uuid),
        'proto':proxy.proto,
        'transport':proxy.transport,
        'proxy_path':hconfig(ConfigEnum.proxy_path),
        'alpn':"h2",
        'extra_info':f'{domain}'
    }

    if base["proto"]=="trojan" and l3!="tls":
        return

    if l3=="http" and  "XTLS" in name:
        return None
    if l3=="http" and base["proto"] in ["ss","ssr"]:
        return 
    

    if "Fake" in name:
        if not hconfig(ConfigEnum.domain_fronting_domain):
            return
        if l3=="http" and not hconfig(ConfigEnum.domain_fronting_http_enable):
            return
        if l3=="tls" and  not hconfig(ConfigEnum.domain_fronting_tls_enable):
            return 
        base['server']=hconfigs[ConfigEnum.domain_fronting_domain]
        base['sni']=hconfigs[ConfigEnum.domain_fronting_domain]
        base["host"]=domain
        base['mode']='Fake'
    elif l3=="http" and not hconfig(ConfigEnum.http_proxy_enable):
        return None    

    ws_path={'vless':f'/{hconfigs[ConfigEnum.proxy_path]}/vlessws',
            'trojan': f'/{hconfigs[ConfigEnum.proxy_path]}/trojanws',
            'vmess':f'/{hconfigs[ConfigEnum.proxy_path]}/vmessws',
            'v2ray':f'/{hconfigs[ConfigEnum.proxy_path]}/v2ray/'
    }
    tcp_path={'vless':f'/{hconfigs[ConfigEnum.proxy_path]}/vltc',
            'trojan': f'/{hconfigs[ConfigEnum.proxy_path]}/trtc',
            'vmess':f'/{hconfigs[ConfigEnum.proxy_path]}/vmtc'
    }
    grpc_service_name={
        'vless':f'{hconfigs[ConfigEnum.proxy_path]}-vlgrpc',
        'vmess':f'{hconfigs[ConfigEnum.proxy_path]}-vmgrpc',
        'trojan': f'{hconfigs[ConfigEnum.proxy_path]}-trgrpc'
    }    

    if base["proto"] in ['v2ray','ss','ssr']:
        base['chipher']='chacha20-ietf-poly1305'
        base['uuid']=f'{hconfig(ConfigEnum.shared_secret)}'

    if base["proto"]=="ssr":
        base["ssr-obfs"]= "tls1.2_ticket_auth"
        base["ssr-protocol"]= "auth_sha1_v4"
        base["fakedomain"]=hconfigs[ConfigEnum.ssr_fakedomain]
        base["mode"]="FakeTLS"
        return base
    elif "faketls" in name:
        base['fakedomain']=hconfig(ConfigEnum.ssfaketls_fakedomain)
        base['mode']='FakeTLS'
        return base
    elif "shadowtls" in name:
        base['fakedomain']=hconfig(ConfigEnum.shadowtls_fakedomain)
        base['mode']='ShadowTLS'
        return base

    if "XTLS" in name:
        base['flow']='xtls-rprx-vision' if proxy.transport=='XTLSVision' else 'xtls-rprx-direct'
        return {**base, 'transport': 'tcp', 'l3': 'xtls', 'alpn':'h2'}
    if "tcp" in name:
        base['transport']='tcp'
        base['path']=tcp_path[base["proto"]]
        return base   
    if proxy.transport in ["ws","WS"]:
        base['transport']='ws'
        base['path']=ws_path[base["proto"]]
        base["host"]=domain
        return base
    if "grpc" in name:
        base['transport']='grpc'
        base['grpc_mode']="multi"
        base['grpc_service_name']=grpc_service_name[base["proto"]]
        return base
    
    if "h1" in name:
        base['transport']= 'tcp'
        base['alpn']='http/1.1'
        return base
    return {'name': name, 'error':True}


def to_link(proxy):
    if 'error' in proxy:return proxy

    name_link=proxy["name"]+"_"+proxy['extra_info']
    if proxy['proto']=='vmess':
        vmess_type= 'http' if proxy["transport"]=='tcp' else 'none'
        return pbase64(f'vmess://{{"v":"2", "ps":"{name_link}", "add":"{proxy["server"]}", "port":"{proxy["port"]}", "id":"{proxy["uuid"]}", "aid":"0", "scy":"auto", "net":"{proxy["transport"]}", "type":"none", "host":"{proxy.get("host","")}", "path":"{proxy["path"] if "path" in proxy else ""}", "tls":"{proxy["l3"]}", "sni":"{proxy["sni"]}"}}')
    if proxy['proto']=="ssr":
        baseurl=f'ssr://proxy["encryption"]:{proxy["uuid"]}@{proxy["server"]}:{proxy["port"]}'
        return None
    if proxy['proto'] in ['ss','v2ray']:
        baseurl=f'ss://proxy["encryption"]:{proxy["uuid"]}@{proxy["server"]}:{proxy["port"]}'
        if proxy['mode']=='faketls':
            return f'{baseurl}?plugin=obfs-local%3Bobfs%3Dtls%3Bobfs-host%3D{proxy["fakedomain"]}&amp;udp-over-tcp=true#{name_link}'
        if proxy['mode']=='shadowtls':
            return f'{baseurl}?plugin=shadow-tls%3Bpassword%3D{proxy["proxy_path"]}%3Bhost%3D{proxy["fakedomain"]}&amp;udp-over-tcp=true#{name_link}'
        if proxy['proto']=='v2ray':
            return f'{baseurl}?plugin=v2ray-plugin%3Bmode%3Dwebsocket%3Bpath%3D{proxy["path"]}%3Bhost%3D{proxy["host"]}%3Btls&amp;udp-over-tcp=true#{name_link}'
    
    infos=f'&sni={proxy["sni"]}&type={proxy["transport"]}'
    if proxy['alpn']!='h2':
        infos+=f'&alpn={proxy["alpn"]}'
    infos+=f'&path={proxy["path"]}' if "path" in proxy else ""
    infos+=f'&host={proxy["host"]}' if "host" in proxy else ""
    if "grpc"==proxy["transport"]:
        infos+=f'&serviceName={proxy["grpc_service_name"]}&mode={proxy["grpc_mode"]}'
    
    infos+=f'#{name_link}'
    baseurl=f'{proxy["proto"]}://{proxy["uuid"]}@{proxy["server"]}:{proxy["port"]}'
    if 'xtls' == proxy['l3']:
        return f'{baseurl}?flow={proxy["flow"]}&security=xtls&type=tcp{infos}'
    if proxy['l3']=='http':
        return f'{baseurl}?security=none{infos}'
    if proxy['l3']=='tls':
        return f'{baseurl}?security=tls{infos}'
    
def to_clash_yml(proxy):
    return yaml.dump(to_clash(proxy))

def to_clash(proxy,meta_or_normal):
    if proxy['l3']=="kcp":return
    if proxy.get('flow','')=="xtls-rprx-vision":return
    if meta_or_normal=="normal":
        if proxy['proto']=="vless":return
        if proxy['l3']=="xtls":return
        if proxy['transport']=="shadowtls":return

    base={}
    # vmess ws
    base["name"]= proxy["name"]
    base["type"]= proxy["proto"]
    base["server"]= proxy["server"]
    base["port"]=proxy["port"]
    if proxy["proto"]=="ssr":
        base["cipher"]= proxy["chipher"]
        base["password"]= proxy["uuid"]
        base["udp"]= True
        base["obfs"]= proxy["ssr-obfs"]
        base["protocol"]= proxy["ssr-protocol"]
        base["obfs-param"]= proxy["fakedomain"]
        return base
    elif proxy["proto"] in ["ss","v2ray"]:
        base["cipher"]= proxy["chipher"]
        base["password"]= proxy["uuid"]
        base["udp_over_tcp"]= True
        if proxy["transport"]=="faketls":
            base["plugin"]= "obfs"
            base["plugin-opts"]={
                "mode": 'tls',
                "host": proxy["fakedomain"]
            }
        elif proxy["transport"]=="shadowtls":
            base["plugin"]= "shadow-tls"
            base["plugin-opts"]={
                "host": proxy["fakedomain"],
                "password": proxy["proxy_path"]
            }
            
        elif proxy["proto"]=="v2ray":
            base["plugin"]= "v2ray-plugin"
            base["type"]="ss"
            base["plugin-opts"]={
                "mode": "websocket",
                "tls": proxy["l3"]=="tls",
                "skip-cert-verify": proxy["mode"]=="FAKE",
                "host": proxy['sni'],
                "path": proxy["path"]
            }
        return base
    elif proxy["proto"]=="trojan":
        base["password"]=proxy["uuid"]
        base["sni"]= proxy["sni"]
    else:
        base["uuid"]= proxy["uuid"]
        base["servername"]= proxy["sni"]
        base["tls"]= proxy["l3"]=="tls"
    if "xtls" == proxy['l3']:
        base["flow"]= proxy['flow']
        base["flow-show"]= True

    if proxy["proto"]=="vmess":
        base["alterId"]= 0
        base["cipher"]= "auto"
    base["udp"]= True
    
    base["skip-cert-verify"]= proxy["mode"]=="FAKE"
    
    
    base["network"]= proxy["transport"]
    
    if base["network"]=="ws":
        base["ws-opts"]={
            "path":proxy["path"]
        }
        if "host" in proxy:
            base["ws-opts"]["headers"]={"Host":proxy["host"]}

    if base["network"]=="tcp":
        # if proxy['proto']=='vless':
        base["network"]="http"    

        if "path" in proxy:
            base["http-opts"]={
                "path": [proxy["path"]]
            }
        
    if base["network"]=="grpc":
        base["grpc-opts"]={
        "grpc-service-name":proxy["grpc_service_name"]
        }
    
   
    return base
    


def get_all_clash_configs(meta_or_normal):
    allp=[]
    for type in all_proxies():
        pinfo=make_proxy(type)
        if pinfo!=None:
            clash=to_clash(pinfo,meta_or_normal)
            if clash:
                allp.append(clash)
    
    return yaml.dump({"proxies":allp},sort_keys=False)
