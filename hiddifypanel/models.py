from sqlalchemy_serializer import SerializerMixin


from flask import Markup
from dateutil import relativedelta
from hiddifypanel.panel.database import db
import enum
import datetime
import uuid as uuid_mod
from enum import auto
from strenum import StrEnum

class ConfigCategory(StrEnum):
    admin=auto()
    branding=auto()
    general=auto()
    proxies=auto()
    domain_fronting=auto()
    telegram=auto()
    http=auto()
    tls=auto()
    ssfaketls=auto()
    shadowtls=auto()
    tuic=auto()
    ssr=auto()
    kcp=auto()
    hidden=auto()

class ConfigEnum(StrEnum):
    lang = auto()
    admin_lang = auto()
    admin_secret = auto()
    tls_ports = auto()
    http_ports = auto()
    kcp_ports = auto()
    kcp_enable = auto()
    decoy_domain = auto()
    proxy_path = auto()
    firewall = auto()
    netdata = auto()
    http_proxy_enable = auto()
    block_iran_sites = auto()
    allow_invalid_sni = auto()
    auto_update = auto()
    speed_test = auto()
    only_ipv4 = auto()

    shared_secret = auto()

    telegram_enable = auto()
    # telegram_secret=auto()
    telegram_adtag = auto()
    telegram_lib = auto()
    telegram_fakedomain = auto()

    v2ray_enable = auto()
    torrent_block = auto()

    ssfaketls_enable = auto()
    # ssfaketls_secret="ssfaketls_secret"
    ssfaketls_fakedomain = auto()

    shadowtls_enable = auto()
    # shadowtls_secret=auto()
    shadowtls_fakedomain = auto()

    tuic_enable = auto()
    tuic_port = auto()

    ssr_enable = auto()
    # ssr_secret="ssr_secret"
    ssr_fakedomain = auto()

    vmess_enable = auto()
    domain_fronting_domain = auto()
    domain_fronting_http_enable = auto()
    domain_fronting_tls_enable = auto()

    db_version = auto()

    branding_title=auto()
    branding_site=auto()
    branding_freetext=auto()
    not_found=auto()
    @classmethod
    def _missing_(cls, value):
      return cls.not_found #"key not found"
    def info(self):
        map = {
            self.branding_title:{'category': ConfigCategory.branding},
            self.branding_site:{'category': ConfigCategory.branding},
            self.branding_freetext:{'category': ConfigCategory.branding},
            self.not_found:{'category': ConfigCategory.hidden},
            self.admin_secret: {'category': ConfigCategory.admin},
            self.lang: {'category': ConfigCategory.branding},
            self.admin_lang: {'category': ConfigCategory.admin},
            self.tls_ports: {'category': ConfigCategory.tls},
            self.http_ports: {'category': ConfigCategory.http},
            self.kcp_ports: {'category': ConfigCategory.kcp},
            self.kcp_enable: {'category': ConfigCategory.kcp,'type':bool},
            self.decoy_domain: {'category': ConfigCategory.general},
            self.proxy_path: {'category': ConfigCategory.hidden},
            self.firewall: {'category': ConfigCategory.general},
            self.netdata: {'category': ConfigCategory.general},
            self.http_proxy_enable: {'category': ConfigCategory.http,'type':bool},
            self.block_iran_sites: {'category': ConfigCategory.proxies,'type':bool},
            self.allow_invalid_sni: {'category': ConfigCategory.tls,'type':bool},
            self.auto_update: {'category': ConfigCategory.general,'type':bool},
            self.speed_test: {'category': ConfigCategory.general,'type':bool},
            self.only_ipv4: {'category': ConfigCategory.general,'type':bool},
            self.torrent_block: {'category': ConfigCategory.general,'type':bool},

            self.shared_secret: {'category': ConfigCategory.proxies},

            self.telegram_enable: {'category': ConfigCategory.telegram,'type':bool},
            # telegram_secret:{'category':'general'},
            self.telegram_adtag: {'category': ConfigCategory.telegram},
            self.telegram_fakedomain: {'category': ConfigCategory.telegram},
            self.telegram_lib: {'category': ConfigCategory.telegram},

            self.v2ray_enable: {'category': ConfigCategory.proxies,'type':bool},

            self.ssfaketls_enable: {'category': ConfigCategory.ssfaketls,'type':bool},
            # ssfaketls_secret:{'category':'ssfaketls'},
            self.ssfaketls_fakedomain: {'category': ConfigCategory.ssfaketls},

            self.shadowtls_enable: {'category': ConfigCategory.shadowtls,'type':bool},
            # shadowtls_secret:{'category':'shadowtls'},
            self.shadowtls_fakedomain: {'category': ConfigCategory.shadowtls},

            self.tuic_enable: {'category': ConfigCategory.tuic,'type':bool},
            self.tuic_port: {'category': ConfigCategory.tuic},

            self.ssr_enable: {'category': ConfigCategory.ssr,'type':bool},
            # ssr_secret:{'category':'ssr'},
            self.ssr_fakedomain: {'category': ConfigCategory.ssr},

            self.vmess_enable: {'category': ConfigCategory.proxies,'type':bool},
            self.domain_fronting_domain: {'category': ConfigCategory.domain_fronting},
            self.domain_fronting_http_enable: {'category': ConfigCategory.domain_fronting},
            self.domain_fronting_tls_enable: {'category': ConfigCategory.domain_fronting},

            self.db_version: {'category': ConfigCategory.hidden},
        }
        return map[self]

    def category(self):
        return self.info()['category']
    def type(self):
        info=self.info()
        return info['type'] if 'type' in info else str


class DomainType(StrEnum):
    direct = auto()
    cdn = auto()
    # fake_cdn = "fake_cdn"
    # telegram_faketls = "telegram_faketls"
    # ss_faketls = "ss_faketls"


class Domain(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain = db.Column(db.String(200), nullable=False, unique=True)
    mode = db.Column(db.Enum(DomainType), nullable=False)


class Proxy(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    enable = db.Column(db.Boolean, nullable=False)
    proto = db.Column(db.String(200), nullable=False)
    l3 = db.Column(db.String(200), nullable=False)
    transport = db.Column(db.String(200), nullable=False)
    cdn = db.Column(db.String(200), nullable=False)


class User(db.Model, SerializerMixin):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(36), default=lambda: str(
        uuid_mod.uuid4()), nullable=False, unique=True)
    # uuid = db.Column(db.UUID(binary=False),default=uuid.uuid4,unique=True,nullable=False)
    name = db.Column(db.String(512), nullable=False)
    # monthly_usage_limit=db.Column(db.BigInteger,default=100,nullable=False)
    # current_usage=db.Column(db.BigInteger,default=0,nullable=False)
    usage_limit_GB = db.Column(db.Numeric(
        6, 9, asdecimal=False), default=1000, nullable=False)
    current_usage_GB = db.Column(db.Numeric(
        6, 9, asdecimal=False), default=0, nullable=False)
    
    monthly=db.Column(db.Boolean,default=False)

    expiry_time = db.Column(
        db.Date, default=datetime.date.today() + relativedelta.relativedelta(months=6))
    last_reset_time = db.Column(db.Date, default=datetime.date.today())


class BoolConfig(db.Model, SerializerMixin):
    # category = db.Column(db.String(128), primary_key=True)
    key = db.Column(db.Enum(ConfigEnum), primary_key=True)
    value = db.Column(db.Boolean)


class StrConfig(db.Model, SerializerMixin):
    # category = db.Column(db.String(128), primary_key=True)
    key = db.Column(db.Enum(ConfigEnum), primary_key=True,   default=ConfigEnum.admin_secret)
    value = db.Column(db.String(2048))


def hdomains(mode):
    domains = Domain.query.filter(Domain.mode == mode).all()
    if domains:
        return [d.domain for d in domains]
    return []


def hdomain(mode):
    domains = hdomains(mode)
    if domains:
        return domains[0]
    return None


def get_hdomains():
    return {mode: hdomains(mode) for mode in DomainType}


def hconfig(key: ConfigEnum):
    try:
        str_conf = StrConfig.query.filter(StrConfig.key == key).first()
        if str_conf:
            return str_conf.value
        bool_conf = BoolConfig.query.filter(BoolConfig.key == key).first()
        if bool_conf:
            return bool_conf.value
        # if key == ConfigEnum.ssfaketls_fakedomain:
        #     return hdomain(DomainType.ss_faketls)
        # if key == ConfigEnum.telegram_fakedomain:
        #     return hdomain(DomainType.telegram_faketls)
        # if key == ConfigEnum.fake_cdn_domain:
        #     return hdomain(DomainType.fake_cdn)
    except:
        print(f'{key} error!')

    return None


def get_hconfigs():
    return {**{u.key: u.value for u in BoolConfig.query.all()},
            **{u.key: u.value for u in StrConfig.query.all()},
            # ConfigEnum.telegram_fakedomain:hdomain(DomainType.telegram_faketls),
            # ConfigEnum.ssfaketls_fakedomain:hdomain(DomainType.ss_faketls),
            # ConfigEnum.fake_cdn_domain:hdomain(DomainType.fake_cdn)
            }
