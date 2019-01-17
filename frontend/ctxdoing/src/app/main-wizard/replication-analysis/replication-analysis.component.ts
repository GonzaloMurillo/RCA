import { Component, OnInit, ViewChild } from '@angular/core';
import { LoggerService } from 'src/app/util/logger.service';
import { BackendService, ReplicationContextAnalysisResult } from 'src/app/backend/backend.service';
import { ErrorDialogComponent } from 'src/app/error-dialog/error-dialog.component';

@Component({
  selector: 'app-replication-analysis',
  templateUrl: './replication-analysis.component.html',
  styleUrls: ['./replication-analysis.component.css']
})
export class ReplicationAnalysisComponent implements OnInit {

  @ViewChild("errorDialog") errorDialog: ErrorDialogComponent;

  replicationContexts: ReplicationContextAnalysisResult[];

  constructor(private log: LoggerService, private backend: BackendService) { }

  ngOnInit() {
    this.populateReplicationContextAnalysisResults();
  }

  populateReplicationContextAnalysisResults() {
    this.backend.getReplicationContextsAnalysisResult().subscribe(
      data => {
        this.log.info("Repl ctx analysis results: ", data);
        this.replicationContexts = data;
      },
      error => {
        this.errorDialog.showError("Failed to analyze the selected replication contexts in the ASUP file: " + error);
      }
    );
  }

}
