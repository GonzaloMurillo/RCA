import { Component, OnInit, ViewChild } from '@angular/core';
import { ErrorDialogComponent } from 'src/app/error-dialog/error-dialog.component';
import { Router } from '@angular/router';

@Component({
  selector: 'app-replication-ctx-selection',
  templateUrl: './replication-ctx-selection.component.html',
  styleUrls: ['./replication-ctx-selection.component.css']
})
export class ReplicationCtxSelectionComponent implements OnInit {

  @ViewChild("errorDialog") errorDialog: ErrorDialogComponent;
  
  selectedRows: any[] = [];
  replicationContexts = [
    {ctx: 1, mtree: '/data/col1/dd390gcsr01_crebm4900_lsu1_rep', destination: 'dd390gcsr01.nam.nsroot.net'},
    {ctx: 2, mtree: '/data/col1/dd390gcsr01_crebm4900_lsu2_rep', destination: 'dd390gcsr01.nam.nsroot.net'},
    {ctx: 3, mtree: '/data/col1/dd390gcsr01_crebm4900_lsu3_rep', destination: 'dd390gcsr01.nam.nsroot.net'}
  ]

  constructor(private router: Router) { }

  ngOnInit() {
    this.selectedRows = this.replicationContexts;
  }

  /**
   * Validate selection of repllication contexts and navigate to the next page
   */
  selectReplicationContextsAndProceed() {
    if (0 == this.selectedRows.length) {
      this.errorDialog.showError("Select at least one replication context to be analyzed");
      return;
    }

    // Navigate to the next page
    this.router.navigate(['replication-analysis']);
  }
}
