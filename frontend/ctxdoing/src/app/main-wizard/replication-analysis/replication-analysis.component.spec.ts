import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ReplicationAnalysisComponent } from './replication-analysis.component';

describe('ReplicationAnalysisComponent', () => {
  let component: ReplicationAnalysisComponent;
  let fixture: ComponentFixture<ReplicationAnalysisComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ReplicationAnalysisComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ReplicationAnalysisComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
