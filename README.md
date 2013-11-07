Remove Orphaned DVS
===================

1. Deploy a new OVF template and point to the desired VSM OVA file (e.g. VSM/Install/nexus-1000v.4.2.1.SV2.2.1a.ova in the archive).

2. Hit Next > Next > Accept > Next > type "tempvsm" and choose the correct datacenter, Next > choose Manually Configure Nexus 1000V, Next > choose a cluster, Next > choose host, Next > choose datastore, Next > Next > choose the correct network label for the Management interface only, Next > don't configure any settings yet, Next > Finish

3. Edit the new VSM's settings and disconnect network adapters 1 and 3

4. Power up the new VSM and proceed with "Configure Temporary VSM" section

5. SSH to the VSM's configured IP address

6. Proceed with "Adding Temporary User" section

## Configure Temporary VSM

1. Answer the following configuration options:

Enter the password for "admin":

Confirm the password for "admin":

Enter HA role[standalone/primary/secondary]: standalone

Enter the domain id<1-4095>: 999

Would you like to enter the basic configuration dialog (yes/no): yes

Create another login account (yes/no) [n]: n

Configure read-only SNMP community string (yes/no) [n]: n

Configure read-write SNMP community string (yes/no) [n]: n

Enter the switch name : switch

Continue with Out-of-band (mgmt0) management configuration? (yes/no) [y]: y

Mgmt0 IPv4 address : 10.21.16.39

Mgmt0 IPv4 netmask : 255.255.252.0

Configure the default gateway? (yes/no) [y]: y

IPv4 address of the default gateway : 10.21.19.254

Configure advanced IP options? (yes/no) [n]: n

Enable the telnet service? (yes/no) [n]: n

Enable the ssh service? (yes/no) [y]: y

Type of ssh key you would like to generate (dsa/rsa) [rsa]: rsa

Number of rsa key bits <768-2048> [1024]: 1024

Enable the http-server? (yes/no) [y]: y

Configure the ntp server? (yes/no) [n]: n

Vem feature level will be set to 4.2(1)SV2(1.1), Do you want to reconfigure? (yes/no) [n]: n

Configure svs domain parameters? (yes/no) [y]: n

Would you like to edit the configuration? (yes/no) [n]: n

Use this configuration and save it? (yes/no) [y]: y

2. Proceed with "Remove Orphaned DVS" section, step 5.

## Adding Temporary User

1. SSH into VSM

2. SSH into an ESX host

3. On ESX host, run: 
```
cat /etc/ssh/ssh_host_rsa_key.pub
```
Example:
```
cat /etc/ssh/ssh_host_rsa_key.pub
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD1OyPq7qIxN4pYPPsgg/5FPu3HPDlw2+sS8dM25883olxP2/JeY/Ta4v+qZctFqDAKCfGVugiS+pRAgpa2t6LqGM54zzv6fgI1pPuZs5m3Smcb2SoAr/LHzC7Sy9yuBRGlC3tp2/ybKZEZQGhc4fH4NIrpIn1rhyH8Lu0f9D+3xQoFSE6Jcg2A1V5rpa+XteSfmR5BsuVpmSWFBzGni9XUOwPgUhyX7vI42uaWtIdGlE6tEHaaSCGHGiGB0bmtlzV6MFrCQS9S++oXKX1Fll1Dq+E+wri/6Lc8ihEIpyPsSLbIaI7EN2Rsef88usZSchgpmwPzjH0TskYjxVy34RwZ
```

4. Copy the output exactly, making sure to avoid extra spaces, carriage returns, etc.

5. On VSM, run (making sure to have pasted the key from the host after the line "username tempuser sshkey" per example):
```
conf t
username tempuser role network-admin
username tempuser sshkey ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD1OyPq7qIxN4pYPPsgg/5FPu3HPDlw2+sS8dM25883olxP2/JeY/Ta4v+qZctFqDAKCfGVugiS+pRAgpa2t6LqGM54zzv6fgI1pPuZs5m3Smcb2SoAr/LHzC7Sy9yuBRGlC3tp2/ybKZEZQGhc4fH4NIrpIn1rhyH8Lu0f9D+3xQoFSE6Jcg2A1V5rpa+XteSfmR5BsuVpmSWFBzGni9XUOwPgUhyX7vI42uaWtIdGlE6tEHaaSCGHGiGB0bmtlzV6MFrCQS9S++oXKX1Fll1Dq+E+wri/6Lc8ihEIpyPsSLbIaI7EN2Rsef88usZSchgpmwPzjH0TskYjxVy34RwZ
```
(When right clicking to paste into the VSM putty window, don't forget to press enter to complete the command.)

6. Proceed with "Delete Extension Key in VC MOB" section

## Delete Extension Key in VC MOB

1. Make note of the extension key on the orphaned DVS's summary tab in VC. (ctrl+shift+n > click the orphaned DVS > copy key from the notes section) It will resemble something like Cisco_Nexus_1000V_792243929.

2. Point a browser to the VC MOB: https://1.2.3.4/mob

3. Login as administrator, or an account with adequate credentials

4. Click content > ExtensionManager > UnregisterExtension

5. Paste the extension key (from step 1) without quotation marks and click Invoke Method (If successful, you'll notice "Method Invocation Result: void" appear on the window in bold letters.) Close MOB windows. If the DVS was previously removed, you're done! Otherwise, proceed to step 6.

6. Proceed with "Configure & Run Python Script on Host" section

## Configure & Run Python Script on Host

1. [Download python script](https://raw.github.com/benperove/remove-orphaned-dvs/master/remove-orphaned-dvs.py)

2. Open script in your favorite text editor and configure USER variables (make sure to use the extension key from Delete Extension Key in VC MOB section, step 1)

3. Copy script to host via SCP or datastore browser

4. SSH to host and make script executable: 
```
chmod a+x /path/to/remove-orphaned-dvs.py
```

5. Execute: 
```
./remove-orphaned-dvs.py -k
```
6. Proceed with "Add Extension Key in VC" section

7. Execute:
```
./remove-orphaned-dvs.py -d
```
8. Confirm orphaned DVS is no longer present in VC inventory

9. Proceed with "Delete Extension Key in VC MOB" section

## Add Extension Key in VC

1. Point a browser to the VSM IP address: http://4.3.2.1

2. Right click the "cisco_nexus_1000v_extension.xml" and save the file to the Desktop

3. From the VC Plug-ins menu, click Manage Plug-ins...

4. Right click in white space below Available Plug-ins and choose New Plug-in...

5. Browse for cisco_nexus_1000v_extension.xml (from step 2) and choose Open > Register Plug-in > Ignore (Security warning) > OK (Success window) > Close (Manage Plug-ins window)

6. Proceed with "Configure & Run Python Script on Host" section, step 7
