import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ReplicationCtxSelectionComponent } from './replication-ctx-selection.component';

describe('ReplicationCtxSelectionComponent', () => {
  let component: ReplicationCtxSelectionComponent;
  let fixture: ComponentFixture<ReplicationCtxSelectionComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ReplicationCtxSelectionComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ReplicationCtxSelectionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
