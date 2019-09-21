(ns zmap
    (:use     [streamparse.specs])
    (:gen-class))

(defn zmap [options]
  [
    ;; spout configuration
    {"kafka-spout" (python-spout-spec
        options
        "spouts.KafkaCons.KafkaMessages"
        ["message"]
    :p 3
        )
    }
    ;; Bolts
    {
        ;; bolt configuration 1
        "country-bolt" (
            python-bolt-spec
            options
            {"kafka-spout" :shuffle}
            "bolts.Country.Country"
            ["msg"]
            :p 4
        )
        "scan-bolt" (
            python-bolt-spec
            options
            {"country-bolt" :shuffle}
            "bolts.ScanCounter.ScanCounter"
            ["msg"]
            :p 1
        )
        "writewebhdfs-bolt" (
            python-bolt-spec
            options
            {"scan-bolt" :shuffle}
            "bolts.WebHDFS.WriteWebHDFS"
            ["msg"]
            :p 2
            :conf {"topology.tick.tuple.freq.secs", 1}
        )
    }
  ]
)
