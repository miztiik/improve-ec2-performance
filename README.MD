# Juice up your EC2 using Jumbo Frames - Maximum Transmission Unit (MTU)

  The maximum transmission unit (MTU) of a network connection is the size, in bytes, of the largest permissible packet that can be passed over the connection. The larger the MTU of a connection, the more data that can be passed in a single packet. Ethernet packets consist of the `frame`, or the actual data you are sending, and the network overhead information that surrounds it.

  You can configure your applications to use bigger frames to take advantage of this feature and improve your application performance. All Amazon EC2 instance types support 1500 MTU, and many current instance sizes support 9001 MTU, or jumbo frames.

![](/images/improve-ec2-performance-with-jumbo-frames.png)

1. ### Premise

    How to test if our new `9000 byte MTU` is actually working and are we reaping the benefits of a larger packet size? We can use `tracepath` to determine the maximum MTU between two endpoints.

    ```sh
     [ec2-user@ip-10-13-0-115 ~]$ tracepath google.com
     1?: [LOCALHOST]                                         pmtu 9001
     1:  ip-10-13-0-1.ec2.internal                             0.226ms pmtu 1500
     1:  no reply
     :
     5:  no reply
     6:  100.65.14.17                                          0.807ms asymm  7 
     7:  52.93.29.63                                          31.645ms asymm  8 
     8:  100.100.2.36                                          0.738ms asymm 12 
     9:  99.82.181.25                                          0.845ms asymm 16 
     10:  no reply
     :
     30:  no reply
         Too many hops: pmtu 1500
         Resume: pmtu 1500 
    ```
    
    In the above route(to the internet) the maximum MTU was 1500, While i do the same with EC2 instances in the same subnet, i am able to achieve a maximum of MTU of 9001

    ```sh
     [ec2-user@ip-10-13-0-115 ~]$ tracepath 10.13.0.126
     1?: [LOCALHOST]                                         pmtu 9001
     :
     30:  no reply
         Too many hops: pmtu 9001
         Resume: pmtu 9001 
    ```
    
    **Can we really use this in a real-world scenario?**

    Let us assume two high I/O intensive EC2 workloads are there in the same subnet. They are processing huge files (~10GBs) between them. We will copy the files between the instances and count how many the _Incoming Packets_ are sent when `MTU 1500` is used and how many are needed when `MTU 9001` is set.
    
2. ### Check the MTU Size
    
    Lets check the current MTU 
    ```sh
    # Set it to to 1500
    sudo ip link set dev eth0 mtu 1500
    ip link show eth0
    ```
3. ### Create a huge file
    
    ```sh
     # Assuming you have 20GB free space
     fallocate -l 20G /home/ec2-user/test.img
    ```

4. ### Send some data

    You can use `scp` or `rsync` to copy the data. I have already copied the private key(`tmp.key`) to allow me to securely copy the data between the machines

    ```sh
    pcksFile="/sys/class/net/eth0/statistics/rx_packets"
    nbPcks=`cat $pcksFile`
    # scp -i tmp.key ec2-user@10.13.0.126:/home/ec2-user/test.img /home/ec2-user/
    rsync -a --info=progress2 \
        -e "ssh -i tmp.key" \
        ec2-user@10.13.0.126:/home/ec2-user/test.img \
        /home/ec2-user/
    echo $(expr `cat $pcksFile` - $nbPcks)
    ```

   *Repeat previous step with mtu set to `9001`*

   ```sh
    sudo ip link set dev eth0 mtu 9001
    ip link show eth0
    pcksFile="/sys/class/net/eth0/statistics/rx_packets"
    nbPcks=`cat $pcksFile`
    # scp -i tmp.key ec2-user@10.13.0.126:/home/ec2-user/test.img /home/ec2-user/
    rsync -a --info=progress2 \
        -e "ssh -i tmp.key" \
        ec2-user@10.13.0.126:/home/ec2-user/test.img \
        /home/ec2-user/
    echo 'Total Incoming Packets: $(expr `cat $pcksFile` - $nbPcks)'
    ```
    _Output_: My experiments with a 20GB file show that, it take about `14860928`packets with MTU 1500 and `2418970`packets with MTU 9001. That is close to 6x improvement.

5. ### Conclusion

    As you can see, you can get almost 6x performance improvements if you configure your applications to make use of the higher `MTU` offered to by AWS and get more out of your EC2 instances.

### Contact Us

You can reach out to us to get more details through [here](https://youtube.com/c/valaxytechnologies/about).

#### References

1. [MTU in Linux](https://docs.aws.amazon.com/en_pv/AWSEC2/latest/UserGuide/network_mtu.html#instance-type-summary-table)
2. [MTU in Windows](https://docs.aws.amazon.com/en_pv/AWSEC2/latest/WindowsGuide/network_mtu.html)
3. [Count Inbound Packets On Interface](https://stackoverflow.com/questions/34231968/count-incoming-packets-on-specific-network-interface)

### Metadata

**Level**: 100
