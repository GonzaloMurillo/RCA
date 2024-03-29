import { Component, OnInit, ViewChild } from '@angular/core';
import { ErrorDialogComponent } from 'src/app/error-dialog/error-dialog.component';
import { Router } from '@angular/router';
import { BackendService, ReplicationContext } from 'src/app/backend/backend.service';
import { LoggerService } from 'src/app/util/logger.service';
import { ClrLoadingState } from '@clr/angular';

@Component({
  selector: 'app-replication-ctx-selection',
  templateUrl: './replication-ctx-selection.component.html',
  styleUrls: ['./replication-ctx-selection.component.css']
})
export class ReplicationCtxSelectionComponent implements OnInit {

  @ViewChild("errorDialog") errorDialog: ErrorDialogComponent;
  
  analyzeButtonLoading = ClrLoadingState.DEFAULT;
  datagridLoading: boolean = true;
  selectedRows: any[] = [];
  replicationContexts: ReplicationContext[];

  constructor(private router: Router, private backend: BackendService, private log: LoggerService) { }

  ngOnInit() {
    this.populateReplicationContextsList();
  }

  populateReplicationContextsList() {
    this.backend.getReplicationContextsList().subscribe(
      data => {
        this.datagridLoading = false;
        this.log.info("Retrieved repl ctx list from backend: ", data);
        this.replicationContexts = data;
        this.selectedRows = this.replicationContexts;
      },
      error => {
        this.datagridLoading = false;
        this.errorDialog.showError("Failed to parse the ASUP file for a list of replication contexts: " + error);
      }
    );
  }

  /**
   * Validate selection of replication contexts and navigate to the next page
   */
  selectReplicationContextsAndProceed() {
    if (0 == this.selectedRows.length) {
      this.errorDialog.showError("Select at least one replication context to be analyzed");
      return;
    }

    this.analyzeButtonLoading = ClrLoadingState.LOADING;
    this.backend.setSelectedReplicationContextsList(this.selectedRows).subscribe(
      data => {
        this.analyzeButtonLoading = ClrLoadingState.SUCCESS;
        this.log.info("Posted selected repl ctx list to backend")
        // Navigate to the next page
        this.router.navigate(['replication-analysis']);
      },
      error => {
        this.analyzeButtonLoading = ClrLoadingState.ERROR;
        this.errorDialog.showError("Failed to select replication contexts for analysis: " + error);
      }
    );
    
  }
}
