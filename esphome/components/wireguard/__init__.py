import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID, CONF_TIME_ID
from esphome.core import CORE
from esphome.components import time

CONF_WG_ADDRESS = "address"
CONF_WG_NETMASK = "netmask"
CONF_WG_PRIVATE_KEY = "private_key"
CONF_WG_PEER_ENDPOINT = "peer_endpoint"
CONF_WG_PEER_PUBLIC_KEY = "peer_public_key"
CONF_WG_PEER_PORT = "peer_port"
CONF_WG_PRESHARED_KEY = "peer_preshared_key"
CONF_WG_KEEPALIVE = "peer_persistent_keepalive"

DEPENDENCIES = ["time"]
CODEOWNERS = ["@lhoracek"]

wireguard_ns = cg.esphome_ns.namespace("wireguard")
Wireguard = wireguard_ns.class_("Wireguard", cg.Component, cg.PollingComponent)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(Wireguard),
        cv.GenerateID(CONF_TIME_ID): cv.use_id(time.RealTimeClock),
        cv.Required(CONF_WG_ADDRESS): cv.string,
        cv.Optional(CONF_WG_NETMASK, default="255.255.255.255"): cv.string,
        cv.Required(CONF_WG_PRIVATE_KEY): cv.string,
        cv.Required(CONF_WG_PEER_ENDPOINT): cv.string,
        cv.Required(CONF_WG_PEER_PUBLIC_KEY): cv.string,
        cv.Optional(CONF_WG_PEER_PORT, default=51820): cv.port,
        cv.Optional(CONF_WG_PRESHARED_KEY): cv.string,
        cv.Optional(CONF_WG_KEEPALIVE): cv.All(cv.positive_int, cv.only_with_esp_idf),
    }
).extend(cv.polling_component_schema("10s"))


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])

    cg.add(var.set_address(config[CONF_WG_ADDRESS]))
    cg.add(var.set_netmask(config[CONF_WG_NETMASK]))
    cg.add(var.set_private_key(config[CONF_WG_PRIVATE_KEY]))
    cg.add(var.set_peer_endpoint(config[CONF_WG_PEER_ENDPOINT]))
    cg.add(var.set_peer_public_key(config[CONF_WG_PEER_PUBLIC_KEY]))
    cg.add(var.set_peer_port(config[CONF_WG_PEER_PORT]))
    if CONF_WG_PRESHARED_KEY in config:
        cg.add(var.set_preshared_key(config[CONF_WG_PRESHARED_KEY]))

    # ESP-IDF section
    if CORE.using_esp_idf:
        cg.add(var.set_srctime(await cg.get_variable(config[CONF_TIME_ID])))

        if CONF_WG_KEEPALIVE in config:
            cg.add(var.set_keepalive(config[CONF_WG_KEEPALIVE]))
        else:
            cg.add(var.set_keepalive(0))

        cg.add_library("https://github.com/droscy/esp_wireguard", None)

    # Arduino section
    else:
        cg.add_library("https://github.com/kienvu58/WireGuard-ESP32-Arduino", "0.1.5")

    await cg.register_component(var, config)
