#!/usr/bin/env python3
import sys
import math

def parse_args(args):
    """Parse command line arguments"""
    params = {}
    for arg in args:
        if '=' in arg:
            key, val = arg.split('=')
            params[key.strip()] = float(val.strip())
    return params

def compute_parameters(params):
    """Compute QoS parameters"""
    r = params.get("r", 10)
    u = params.get("u", 100000)
    T = params.get("T", 1e8)
    w = params.get("w", 0.5)

    retrans_ns = int(1e9 / (2 * r))
    history_cache = math.floor(T / u)

    return {
        "r": int(r),
        "u": int(u),
        "T": int(T),
        "w": w,
        "retrans_ns": retrans_ns,
        "history_cache": history_cache
    }

def generate_publisher_xml(params, output_file):
    """Generate Publisher XML"""
    xml_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
<dds xmlns="http://www.eprosima.com">
    <profiles>
        <transport_descriptors>
            <transport_descriptor>
                <transport_id>udp_transport</transport_id>
                <type>UDPv4</type>
                <maxMessageSize>1472</maxMessageSize>
            </transport_descriptor>
        </transport_descriptors>
        <participant profile_name="optimizer_participant_pub_profile" is_default_profile="true">
            <rtps>
                <userTransports>
                    <transport_id>udp_transport</transport_id>
                </userTransports>
                <useBuiltinTransports>false</useBuiltinTransports>
            </rtps>
        </participant>
        <publisher profile_name="optimizer_publisher_profile" is_default_profile="true">
            <topic>
                <historyQos>
                    <kind>KEEP_ALL</kind>
                </historyQos>
                <resourceLimitsQos>
                    <max_samples>{params['history_cache']}</max_samples>
                    <max_instances>10</max_instances>
                    <max_samples_per_instance>{params['history_cache']}</max_samples_per_instance>
                </resourceLimitsQos>
            </topic>
            <qos>
                <disable_heartbeat_piggyback>true</disable_heartbeat_piggyback>
                <reliability>
                    <kind>RELIABLE</kind>
                    <max_blocking_time>
                        <sec>1000</sec>
                    </max_blocking_time>
                </reliability>
            </qos>
            <times>
                <initialHeartbeatDelay>
                    <nanosec>0</nanosec>
                </initialHeartbeatDelay>
                <heartbeatPeriod>
                    <sec>0</sec>
                    <nanosec>{params['retrans_ns']}</nanosec>
                </heartbeatPeriod>
                <nackResponseDelay>
                    <nanosec>0</nanosec>
                </nackResponseDelay>
                <nackSupressionDuration>
                    <sec>0</sec>
                </nackSupressionDuration>
            </times>
        </publisher>
    </profiles>
</dds>
"""
    with open(output_file, "w") as f:
        f.write(xml_content)
    print(f"[INFO] Publisher XML: {output_file}")

def generate_subscriber_xml(params, output_file):
    """Generate Subscriber XML"""
    xml_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
<dds xmlns="http://www.eprosima.com">
   <profiles>
        <transport_descriptors>
            <transport_descriptor>
                <transport_id>udp_transport</transport_id>
                <type>UDPv4</type>
                <maxMessageSize>1472</maxMessageSize>
            </transport_descriptor>
        </transport_descriptors>
        <participant profile_name="optimizer_participant_sub_profile" is_default_profile="true">
            <rtps>
                <userTransports>
                    <transport_id>udp_transport</transport_id>
                </userTransports>
                <useBuiltinTransports>false</useBuiltinTransports>
            </rtps>
        </participant>
        <subscriber profile_name="optimizer_subscriber_profile" is_default_profile="true">
            <topic>
                <resourceLimitsQos>
                    <max_samples>{params['history_cache']}</max_samples>
                    <max_instances>10</max_instances>
                    <max_samples_per_instance>{params['history_cache']}</max_samples_per_instance>
                </resourceLimitsQos>
            </topic>
            <qos>
                <liveliness>
                    <kind>AUTOMATIC</kind>
                    <lease_duration>
                        <sec>DURATION_INFINITY</sec>
                    </lease_duration>
                    <announcement_period>
                        <sec>DURATION_INFINITY</sec>
                    </announcement_period>
                </liveliness>
            </qos>
            <times>
                <initialAcknackDelay>
                    <sec>0</sec>
                    <nanosec>0</nanosec>
                </initialAcknackDelay>
                <heartbeatResponseDelay>
                    <sec>0</sec>
                    <nanosec>0</nanosec>
                </heartbeatResponseDelay>
            </times>
        </subscriber>
    </profiles>
</dds>
"""
    with open(output_file, "w") as f:
        f.write(xml_content)
    print(f"[INFO] Subscriber XML: {output_file}")

def main():
    required_keys = {"r", "u", "T", "w"}

    if len(sys.argv) < 2:
        print("Usage: python3 DDS_Optimizer.py r=30 u=330000 T=90000000 w=0.6")
        sys.exit(1)

    args = parse_args(sys.argv[1:])
    if not required_keys.issubset(args.keys()):
        print("Usage: python3 DDS_Optimizer.py r=30 u=330000 T=90000000 w=0.6")
        sys.exit(1)

    qos = compute_parameters(args)
    pub_filename = "Optimized_profile_pub.xml"
    sub_filename = "Optimized_profile_sub.xml"

    generate_publisher_xml(qos, pub_filename)
    generate_subscriber_xml(qos, sub_filename)

    print(f"[INFO] HistoryCache_size = {qos['history_cache']} | Retransmission_ns = {qos['retrans_ns']}")

if __name__ == "__main__":
    main()

