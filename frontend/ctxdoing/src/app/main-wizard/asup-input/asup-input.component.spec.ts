import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AsupInputComponent } from './asup-input.component';

describe('AsupInputComponent', () => {
  let component: AsupInputComponent;
  let fixture: ComponentFixture<AsupInputComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AsupInputComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AsupInputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
