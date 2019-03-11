import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { LoggerService } from 'src/app/util/logger.service';
import { BackendService, ReplicationContextAnalysisResult } from 'src/app/backend/backend.service';
import { ErrorDialogComponent } from 'src/app/error-dialog/error-dialog.component';
import {colorSets} from 'src/app/util/ngx-charts-color-schemes';

@Component({
  selector: 'app-replication-analysis',
  templateUrl: './replication-analysis.component.html',
  styleUrls: ['./replication-analysis.component.css']
})
export class ReplicationAnalysisComponent implements AfterViewInit {

  @ViewChild("errorDialog") errorDialog: ErrorDialogComponent;

  replicationContexts: ReplicationContextAnalysisResult[];

  showChart: boolean = false;
  chartColorScheme: any = colorSets[0];
  chartData: any[] = [];

  constructor(private log: LoggerService, private backend: BackendService) { }

  ngAfterViewInit() {
    this.populateReplicationContextAnalysisResults();
  }

  formatChartLabel(original: any) {
    console.log(original);

    return original.value;
  }

  populateReplicationContextAnalysisResults() {
    this.backend.getReplicationContextsAnalysisResult().subscribe(
      data => {
        this.log.info("Repl ctx analysis results: ", data);
        this.replicationContexts = data;
        this.replicationContexts.forEach(ctx => {
          let chart = [];
          ctx.ctxUsageTime.forEach(e => {
            if (e.unit === '%') {
              chart.push({
                name: e.key.replace("Time ", ""),
                value: e.value
              });
            }
          });
          this.chartData.push(chart);
        });
        this.showChart = true;
      },
      error => {
        this.errorDialog.showError("Failed to analyze the selected replication contexts in the ASUP file: " + error);
      }
    );
  }

}
