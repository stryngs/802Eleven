Spin up a Python3 virtual env and then:
```
git clone https://github.com/stryngs/packetEssentials
git clone https://github.com/stryngs/easy-thread
git clone https://github.com/stryngs/quickset

python3 -m pip install packetEssentials/RESOURCEs/*.tar.gz
python3 -m pip install easy-thread/*.tar.gz
python3 -m pip install quickset/lib/SRC/quickset*
```

Now do:
```
python3 ./pmkid2hashcat.py -i <Monitor Mode NIC>
```

pmkid2hashcat does not inject if the outcome is already known.  Once you have a captured string that is the input for hashcat, there is no sense in making duplicates, nor interacting with the same ESSID again.  This simplicity also means that if you miss a PMKID due to something such as perhaps a channel switch; pmkid2hashcat will not retry.

The simplistic nature of pmkid2hashcat is by design.  Be seen the least amount of times as possible.  All the tools for this method I have found online seem to inject where no such thing is required.  These tools are loud.  pmkid2hashcat is silent.

hashes.file is for hashcat, hashes.log is for humans.  Both logs are appended to and never overwritten.

pmkid2hashcat does not control or care about channel hopping.  An easy way to hop channels without too much work is simply utilizing airodump-ng at the same time.  Let airodump-ng control the hops and pmkid2hashcat prepare the hashes for hashcat intake without having to do a conversion that a tool like hcxdumptool requires.

This software is still in very much a testing phase as I took a lot of shortcuts in getting the Association Request frame correct.  What worked in the limited environment I setup may very well not work in another.  If you find that a tool like hcxdumptool captures PMKID where pmkid2hashcat does not, please open an issue.
