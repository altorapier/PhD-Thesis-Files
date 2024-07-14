int x;
int s;
int incoming[1];
int StepsW1 = 1;
int StepsW2 = 1;
int PositionW1 = 0;
int PositionW2 = 0;
boolean DirectionW1 = true;
boolean DirectionW2 = true;
void stepperW1(int xw ); 
void stepperW2(int xw ); 
void setup() 
{
  Serial.begin(9600);
  Serial.setTimeout(1);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  
  stepperStopW1();
  stepperStopW2();
}



void stepperStopW1()
{
  digitalWrite(2, LOW);
  digitalWrite(3, LOW);
  digitalWrite(4, LOW);
  digitalWrite(5, LOW);
}
void stepperStopW2()
{
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  digitalWrite(8, LOW);
  digitalWrite(9, LOW);
}
void loop() 
{
  while (Serial.available() >= 2)
  {

    s = Serial.read();
    x = Serial.read();
    Serial.write(s);
    Serial.write(x);
    
    if (s == 1)
    {
      if((x >= 0) && (x<6))
      {
        if (x > PositionW1)
        {
          DirectionW1 = true;
          stepperW1(round((x - PositionW1)*682.5));
          stepperStopW1();
          //stepper(682);
        }
        else
        {
          DirectionW1 = false;
          stepperW1(round((PositionW1 - x)*682.5));
          stepperStopW1();
        }
        PositionW1 = x;
        //stepperStop();
      }
    }
    if (s == 2)
    {
      if((x >= 0) && (x<6))
      {
        if (x > PositionW2)
        {
          DirectionW2 = true;
          stepperW2(round((x - PositionW2)*682.5));
          stepperStopW2();
          //stepper(682);
        }
        else
        {
          DirectionW2 = false;
          stepperW2(round((PositionW2 - x)*682.5));
          stepperStopW2();
        }
        PositionW2 = x;
        //stepperStop();
      }
    }
  }
}

void stepperW1(int xw) 
{
     for (int x = 0; x < xw; x++) {
      delayMicroseconds(2000);
        switch (StepsW1) {
             case 0:
                  digitalWrite(2, LOW);
                  digitalWrite(3, LOW);
                  digitalWrite(4, LOW);
                  digitalWrite(5, HIGH);
                  break;
             case 1:
                  digitalWrite(2, LOW);
                  digitalWrite(3, LOW);
                  digitalWrite(4, HIGH);
                  digitalWrite(5, HIGH);
                  break;
             case 2:
                  digitalWrite(2, LOW);
                  digitalWrite(3, LOW);
                  digitalWrite(4, HIGH);
                  digitalWrite(5, LOW);
                  break;
             case 3:
                  digitalWrite(2, LOW);
                  digitalWrite(3, HIGH);
                  digitalWrite(4, HIGH);
                  digitalWrite(5, LOW);
                  break;
             case 4:
                  digitalWrite(2, LOW);
                  digitalWrite(3, HIGH);
                  digitalWrite(4, LOW);
                  digitalWrite(5, LOW);
                  break;
             case 5:
                  digitalWrite(2, HIGH);
                  digitalWrite(3, HIGH);
                  digitalWrite(4, LOW);
                  digitalWrite(5, LOW);
                  break;
             case 6:
                  digitalWrite(2, HIGH);
                  digitalWrite(3, LOW);
                  digitalWrite(4, LOW);
                  digitalWrite(5, LOW);
                  break;
             case 7:
                  digitalWrite(2, HIGH);
                  digitalWrite(3, LOW);
                  digitalWrite(4, LOW);
                  digitalWrite(5, HIGH);
                  break;
             default:
                  digitalWrite(2, LOW);
                  digitalWrite(3, LOW);
                  digitalWrite(4, LOW);
                  digitalWrite(5, LOW);
                  break;
                  }
       SetDirectionW1();
      }
}

void stepperW2(int xw) 
{
     for (int x = 0; x < xw; x++) 
     {
      delayMicroseconds(2000);
        switch (StepsW2) 
        {
             case 0:
                  digitalWrite(6, LOW);
                  digitalWrite(7, LOW);
                  digitalWrite(8, LOW);
                  digitalWrite(9, HIGH);
                  break;
             case 1:
                  digitalWrite(6, LOW);
                  digitalWrite(7, LOW);
                  digitalWrite(8, HIGH);
                  digitalWrite(9, HIGH);
                  break;
             case 2:
                  digitalWrite(6, LOW);
                  digitalWrite(7, LOW);
                  digitalWrite(8, HIGH);
                  digitalWrite(9, LOW);
                  break;
             case 3:
                  digitalWrite(6, LOW);
                  digitalWrite(7, HIGH);
                  digitalWrite(8, HIGH);
                  digitalWrite(9, LOW);
                  break;
             case 4:
                  digitalWrite(6, LOW);
                  digitalWrite(7, HIGH);
                  digitalWrite(8, LOW);
                  digitalWrite(9, LOW);
                  break;
             case 5:
                  digitalWrite(6, HIGH);
                  digitalWrite(7, HIGH);
                  digitalWrite(8, LOW);
                  digitalWrite(9, LOW);
                  break;
             case 6:
                  digitalWrite(6, HIGH);
                  digitalWrite(7, LOW);
                  digitalWrite(8, LOW);
                  digitalWrite(9, LOW);
                  break;
             case 7:
                  digitalWrite(6, HIGH);
                  digitalWrite(7, LOW);
                  digitalWrite(8, LOW);
                  digitalWrite(9, HIGH);
                  break;
             default:
                  digitalWrite(6, LOW);
                  digitalWrite(7, LOW);
                  digitalWrite(8, LOW);
                  digitalWrite(9, LOW);
                  break;
                  }
       SetDirectionW2();
      }
}

void SetDirectionW1() 
{
    if (DirectionW1 == 1) 
    {
        StepsW1++;
    }
    if (DirectionW1 == 0) 
    {
        StepsW1--;
    }
    if (StepsW1 > 7) 
    {
        StepsW1 = 0;
    }
    if (StepsW1 < 0) 
    {
        StepsW1 = 7;
    }
} 
void SetDirectionW2() 
{ //1 to 7 stepper cycles
    if (DirectionW2 == 1) 
    {
        StepsW2++;
    }
    if (DirectionW2 == 0) {
        StepsW2--;
    }
    if (StepsW2 > 7) {
        StepsW2 = 0;
    }
    if (StepsW2 < 0) {
        StepsW2 = 7;
    }
}  
