"""Mandatory raw evidence validators; declarations never synthesize native facts."""
from gate import need
from validators import fullscreen_ancestor

def fullscreen_certificate(pristine,core):
 # Offline-only certificate: no calibration client or full-screen run is started.
 for record in (pristine,core):
  ancestor=fullscreen_ancestor(record["owner_path"])
  need(record["native_xdg"] is True and record["configure_ack"]>0,"normal XDG configure/ACK")
  children=ancestor["nodes"]
  need(len(children)>=2 and record["owner_id"] in {x["id"] for x in children},"nonleaf direct children")
  need(record["configure"][0]>0 and record["configure"][1]>0,"configure dimensions")
  a,b=record["popup_A"],record["popup_B"]
  need(a[0]<record["boundary"]<a[0]+a[2] and b[0]<record["boundary"]<b[0]+b[2],"real plausible crossing")
 need(pristine["configure"]==core["configure"] and pristine["child_configures"]==core["child_configures"],"noncomparable fullscreen children/configure")
 return dict(status="OFFLINE_CERTIFICATE_ONLY",runtime="NOT_RUN")

def native_present(commits,presents):
 # Correlation requires an actual native event and exact run/output/sequence key.
 keys=set()
 for event in commits:
  need(event.get("source")=="native-output-commit" and event.get("native_event") is True,"fake commit")
  key=(event["run"],event["output"],event["commit_seq"]);need(key not in keys,"duplicate commit key");keys.add(key)
 seen=set()
 for event in presents:
  need(event.get("source")=="native-output-present" and event.get("native_event") is True,"fake present")
  key=(event["run"],event["output"],event["commit_seq"])
  need(key in keys and key not in seen,"unmatched/duplicate native present");seen.add(key)
 return dict(matched=len(seen),unmatched_commits=len(keys-seen),gpu_completion="NOT_PROVEN",native_buffer_identity="NOT_PROVEN",atomic_generation="NOT_PROVEN")
