import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-replication-analysis',
  templateUrl: './replication-analysis.component.html',
  styleUrls: ['./replication-analysis.component.css']
})
export class ReplicationAnalysisComponent implements OnInit {

  replicationContexts = [
    {
      ctx: 1,
      mtree: '/data/col1/dd390gcsr01_crebm4900_lsu1_rep',
      destination: 'dd390gcsr01.nam.nsroot.net',
      graphImage: 'assets/replicationgraph.png',
      ctxUsageTime: [
        { "key": "Total time spent by the replication context", "value": "11362471 seconds" },
        { "key": "Time sending references", "value": "0.2" },
        { "key": "Time sending segments", "value": "1.5" },
        { "key": "Time receiving references", "value": "0.4" },
        { "key": "Time waiting for references from destination", "value": "1.4" },
        { "key": "Time waiting getting references", "value": "2.9" },
        { "key": "Time local reading segments", "value": "93.6" },
        { "key": "Time sending small files", "value": "0.0" },
        { "key": "Time sending sketches", "value": "0.0" },
        { "key": "Time receiving bases", "value": "0.0" },
        { "key": "Time reading bases", "value": "0.0" },
        { "key": "Time getting chunk info", "value": "0.0" },
        { "key": "Time unpacking chunks of info", "value": "0.0" }
      ]
    },
    {
      ctx: 2,
      mtree: '/data/col1/dd390gcsr01_crebm4900_lsu2_rep',
      destination: 'dd390gcsr01.nam.nsroot.net',
      graphImage: 'assets/replicationgraph.png',
      ctxUsageTime: [
        { "key": "Total time spent by the replication context", "value": "11362471 seconds" },
        { "key": "Time sending references", "value": "0.2" },
        { "key": "Time sending segments", "value": "1.5" },
        { "key": "Time receiving references", "value": "0.4" },
        { "key": "Time waiting for references from destination", "value": "1.4" },
        { "key": "Time waiting getting references", "value": "2.9" },
        { "key": "Time local reading segments", "value": "93.6" },
        { "key": "Time sending small files", "value": "0.0" },
        { "key": "Time sending sketches", "value": "0.0" },
        { "key": "Time receiving bases", "value": "0.0" },
        { "key": "Time reading bases", "value": "0.0" },
        { "key": "Time getting chunk info", "value": "0.0" },
        { "key": "Time unpacking chunks of info", "value": "0.0" }
      ]
    },
    {
      ctx: 3,
      mtree: '/data/col1/dd390gcsr01_crebm4900_lsu3_rep',
      destination: 'dd390gcsr01.nam.nsroot.net',
      graphImage: 'assets/replicationgraph.png',
      ctxUsageTime: [
        { "key": "Total time spent by the replication context", "value": "11362471 seconds" },
        { "key": "Time sending references", "value": "0.2" },
        { "key": "Time sending segments", "value": "1.5" },
        { "key": "Time receiving references", "value": "0.4" },
        { "key": "Time waiting for references from destination", "value": "1.4" },
        { "key": "Time waiting getting references", "value": "2.9" },
        { "key": "Time local reading segments", "value": "93.6" },
        { "key": "Time sending small files", "value": "0.0" },
        { "key": "Time sending sketches", "value": "0.0" },
        { "key": "Time receiving bases", "value": "0.0" },
        { "key": "Time reading bases", "value": "0.0" },
        { "key": "Time getting chunk info", "value": "0.0" },
        { "key": "Time unpacking chunks of info", "value": "0.0" }
      ]
    }
  ]

  constructor() { }

  ngOnInit() {
  }

}
