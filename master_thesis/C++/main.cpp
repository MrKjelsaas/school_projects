
#include <iostream>
#include <vector>
#include <thread>

#include "Eigen/Dense"
#include "otter/otter.h"
#include "ship_dynamics/ship_dynamics_functions.h"





using namespace std;
using namespace Eigen;
using Eigen::MatrixXd;






int main() {



  MatrixXd my_matrix(3, 3);
  int k = 0;
  for (int i = 0; i <3; i++){
    for (int j = 0; j <3; j++){
      my_matrix(i, j) = k;
      k++;
    }
  }



  vector<MatrixXd> my_vector = {my_matrix};

  cout << "..." << endl;

  for (MatrixXd x : my_vector){
    cout << x << endl;
  }

  cout << "..." << endl;

  my_matrix.resize(4, 4);
  my_matrix(2, 3) = 9;
  my_matrix(2, 2) = 6;

  my_vector.push_back(my_matrix);

  for (MatrixXd x : my_vector){
    cout << x << endl;
  }

  cout << "..." << endl;

  my_vector.erase(my_vector.begin()+0);

  for (auto x : my_vector){
    cout << x << endl;
  }

  cout << "..." << endl;




































/* Testing Otter communication
  otter_usv the_otter;

  if (not the_otter.establish_connection()){
    cout << "Couldn't establish connection to Otter" << endl;
    return -1;
  };

  the_otter.send_message("ABC123");
  string message_from_otter = the_otter.read_message();
  cout << "Received message from Otter: " << message_from_otter << endl;

  the_otter.set_leg_mode(59.908260, 108.719523, -59.908260, -108.719523, 1);
  sleep(3);
  the_otter.set_leg_mode(-59.908260, -108.719523, 59.908260, 108.719523, 1);
  sleep(3);
  the_otter.set_station_mode(59.908260, 108.719523, 1);
  sleep(3);
  the_otter.set_station_mode(-59.908260, -108.719523, 1);

  the_otter.close_connection();
*/



  return 0;
}
