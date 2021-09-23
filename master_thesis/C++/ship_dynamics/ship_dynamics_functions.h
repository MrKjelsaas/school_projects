
#include <cmath>



float froude_number(float U, float L){
  return U / sqrt(9.81*L);
}
