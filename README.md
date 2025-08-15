# DDS Optimizer for Wirelss Large Payload Transfer
<p align="center">
  <img alt="ROS2 logo" src="https://img.shields.io/badge/ROS--2-Humble-blue?style=for-the-badge">
  <img alt="Fast DDS logo" src="https://img.shields.io/badge/Fast--DDS-2.6.9-brightgreen?style=for-the-badge">
</p>


## 📝 Paper Summary
ROS 2 uses a DDS-based communication stack, but suffers from severe performance degradation when transmitting large payloads over wireless networks. The key root causes are identified as IP fragmentation, inefficient retransmission timing, and buffer bursts. To address these issues, the paper proposes a lightweight optimization framework that leverages only XML-based QoS configuration without modifying the DDS protocol. The optimization consists of: (i) setting the RTPS message size to 1472 B, (ii) configuring the retransmission rate as *n* = *2r*, and (iii) adjusting the HistoryCache size based on payload size *u* and link bandwidth. All improvements are fully compatible with existing ROS 2 applications and require no changes to application logic or middleware internals. Experiments were conducted on ROS 2 Humble using Fast DDS 2.6.9 version over IEEE 802.11ac wireless links. Test scenarios included different packet error rates (1%, 20%), temporary link outages, and varying payload sizes (32–512 KB). Default DDS and LARGE_DATA mode failed to maintain performance under high loss, while the proposed optimization remained stable up to 512 KB. The effectiveness of HistoryCache tuning was particularly evident in link outage recovery scenarios. Overall, this work demonstrates that practical, protocol-compliant DDS tuning enables robust and real-time wireless communication in ROS 2.

## Essential QoS Settings for Topic Communication
| QoS Policy| QoS Value | Function | 
|------|---------|---------|
| **history** | **KEEP_ALL** | To store all data without loss |
| **reliability** | **RELIABLE** | To ensure that every message sample is delivered without loss |
| **reliability.max_blocking_time** | **A sufficiently large value** | To prevent publisher blocking or data loss |

## About DDS Optimizer
Our forthcoming paper introduces an optimizer for configuring parameters to efficiently transmit large payloads.

> **Input**: Publish rate *r*, payload size *u*, link-layer throughput *T*<sub>OS→Link</sub>, link utilization 𝜔  
> **Step 1**: **Prevents IP fragmentation** Set RTPS maxMessageSize = 1472 B  
> **Step 2**: **Minimize Retransmission Jitter** Set retransmission rate *n* = *2r*   
> **Step 3**: **Prevent Buffer Burst** Set HistoryCache size as <div align="center"> <img width="169" height="56" alt="image" src="https://github.com/user-attachments/assets/e95dfebe-7b2a-4076-bee3-71e8b73491cb" /></div>
> **Output**: Optimized ROS 2 XML QoS profile

### XML Configuration Details

Each optimization step is implemented through specific XML configurations:

**Step 1: Prevents IP fragmentation**

> **XML Configuration:**
> ```xml
> <transport_descriptor>
>     <transport_id>udp_transport</transport_id>
>     <type>UDPv4</type>
>     <maxMessageSize>1472</maxMessageSize>
> </transport_descriptor>
> ```

This setting limits the RTPS message size to 1472 bytes to prevent IP fragmentation over wireless networks.

**Step 2: Minimize Retransmission Jitter**

> **XML Configuration:**
> ```xml
> <heartbeatPeriod>
>     <sec>0</sec>
>     <nanosec>[Optimized Value]</nanosec>
> </heartbeatPeriod>
> ```

The heartbeat period is optimized to `n = 2r` where `r` is the publish rate, reducing retransmission jitter and improving control traffic efficiency.

**Step 3: Prevent Buffer Burst**

> **XML Configuration:**
> ```xml
> <resourceLimitsQos>
>     <max_samples>[Optimized Value]</max_samples>
>     <max_instances>10</max_instances>
>     <max_samples_per_instance>[Optimized Value]</max_samples_per_instance>
> </resourceLimitsQos>
> ```

The HistoryCache size is calculated as `⌊T × ω / u⌋` where:
- `T` is the link-layer throughput
- `ω` is the link utilization (default: 0.6-0.7, reduce for congested links)
- `u` is the payload size

This prevents buffer overflow and ensures stable data transmission by considering actual available bandwidth.


## 💡 How to run it from the terminal

### Step-by-Step Guide

#### 1. Navigate to your ROS 2 package directory
```bash
# Example: Navigate to ROS 2 package on Ubuntu
cd ~/ros2_ws/src/your_package_name
```

#### 2. Verify that your code satisfies the Essential QoS Settings

**Python version (rclpy):**
```python
qos = QoSProfile(
    history=HistoryPolicy.KEEP_ALL,
    reliability=ReliabilityPolicy.RELIABLE
)
# Publisher
publisher = node.create_publisher(String, 'topic_name', qos)

# Subscriber
subscriber = node.create_subscription(String, 'topic_name', callback, qos)
```

**C++ version (rclcpp):**
```cpp
auto qos = rclcpp::QoS(10)
    .keep_all()
    .reliable();

// Publisher
auto publisher = node->create_publisher<std_msgs::msg::String>("topic_name", qos);

// Subscriber
auto subscriber = node->create_subscription<std_msgs::msg::String>(
    "topic_name", qos, callback);
```

#### 3. Clone DDS Optimizer and navigate to the optimizer directory
```bash
git clone https://github.com/anonymous-ld/large-data-optimization.git
cd large-data-optimization
```

#### 4. Run DDS_Optimizer.py
```bash
# Basic usage
python3 DDS_Optimizer.py r={publish rate} u={payload size} T={link-layer throughput} w={link utilization}

# Example: [publish rate = 30 Hz], [payload size = 330 KB], [link-layer throughput = 90 Mb/s], [link utilization = 0.6]
python3 DDS_Optimizer.py r=30 u=330000 T=90000000 w=0.6
```

**Output example:**
```
[INFO] Publisher XML: Optimized_profile_pub.xml
[INFO] Subscriber XML: Optimized_profile_sub.xml
[INFO] HistoryCache_size = 309 | Retransmission_ns = 16666666
```

#### 5. Apply the generated XML to your pub and sub

**5-1. Set as default XML using environment variables (Recommended)**
```bash
# Linux/macOS
export FASTRTPS_DEFAULT_PROFILES_FILE=/path/to/generated_pub.xml
```

**5-2. Set the generated XML as default XML in your code**
```python
# Set environment variable in Python
import os
os.environ['FASTRTPS_DEFAULT_PROFILES_FILE'] = '/path/to/generated_pub.xml'
```

```cpp
// Set environment variable in C++
#include <cstdlib>
setenv("FASTRTPS_DEFAULT_PROFILES_FILE", "/path/to/generated_pub.xml", 1);
```

## Performance Comparision
<div align="center">
  <img src="https://github.com/user-attachments/assets/c5b10170-74ac-4b8a-a0e7-9dc8ac82e742" alt="table2" width="600">
</div>


## 📢 Notice
This project is currently compatible with ROS 2 Humble using Fast DDS 2.6.9.
Support for other DDS vendors such as Cyclone DDS and OpenDDS is planned in future updates.

### Contact & Collaboration
If you have any issues or questions about using this tool, please feel free to contact us anytime.

**Email**: [leesh2913@dgist.ac.kr](mailto:leesh2913@dgist.ac.kr)  
**Homepage**: [hun0130.github.io](https://hun0130.github.io/)

Research collaborations and industry-academia partnerships are also welcome!

