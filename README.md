# ztrack
A cross-platform time-tracking tool that sits in the system tray.  
  
Currently, no labels (called "activities" on the user end) are added during installation. To add labels, edit the labels file `[application data directory]/mmatlin/ztrack/labels.yaml`. (On Windows, the application data directory would be `C:\Users\[username]\AppData\Roaming\mmatlin\ztrack`.) The format of `labels.yaml` should follow this example:
```
Homework:
  record_type: item
Projects:
  record_type: item
Internship:
  record_type: item
```
Currently, label groups are not supported. For this reason, all labels should have a `record_type` of item.  
  
To add a default label, change `label` and `record_type` in `default_label_info` in `state.yaml` accordingly. An example of this could look like:  
```
...
default_label_info:
  label: Internship
  record_type: item
...
```
Tracked time can be found in `records.yaml`. Later on, the user will be able to access recorded time-tracking data graphically.  
  
⏱