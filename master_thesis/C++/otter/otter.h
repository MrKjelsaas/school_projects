
#include <iostream>
#include <sys/types.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>
#include <string>



using namespace std;





string checksum(string message){
  char the_checksum = 0;

  for (int n = 0; n < message.size(); n++){
    the_checksum ^= message[n];
  }

  stringstream stream;
  stream << hex << int(the_checksum);
  return stream.str();
}





class otter_usv {

private:

  // Create a socket for TCP communication
  int sock = socket(AF_INET, SOCK_STREAM, 0);

  float current_latitude;
  float current_longitude;
  float current_time;
  float current_angle;
  float current_speed;
  float fuel_capacity;

  const float home_latitude = 59.908576;
  const float home_longitude = 10.719615;

  float top_speed;

  bool connection_status;

  string last_message_received;



public:

  bool establish_connection(){
    cout << "Attempting to connect to Otter" << endl;

    if (sock == -1){
        return false;
    }

    //	Create a hint structure for the server we're connecting with
    int destination_port = 2009;
    string destination_ip = "192.168.53.xx";
    destination_ip = "127.0.0.1";

    sockaddr_in hint;
    hint.sin_family = AF_INET;
    hint.sin_port = htons(destination_port);
    inet_pton(AF_INET, destination_ip.c_str(), &hint.sin_addr);

    //	Connect to the server on the socket
    int connectRes = connect(sock, (sockaddr*)&hint, sizeof(hint));
    if (connectRes == -1){
      return false;
    }

    cout << "Successfully connected to Otter" << endl;
    connection_status = true;
    return true;
  }



  bool close_connection(){
    cout << "Disconnecting from Otter" << endl;
    connection_status = false;
    close(sock);
    return true;
  }



  bool should_be_connected(){
    return connection_status;
  }



  string read_message(){
    char buf[4096];
    string received_message;
    memset(buf, 0, 4096);

    fd_set fd;
    timeval tv;
    tv.tv_sec = 5;
    tv.tv_usec = 0;
    FD_ZERO(&fd);
    FD_SET(sock, &fd);

    int bytes_received;
    int receiving_status = select(sock+1, &fd, NULL, NULL, &tv);
    if (receiving_status > 0){
      bytes_received = recv(sock, buf, 4096, 0);
      if (bytes_received == -1){
          cout << "There was an error getting response from the Otter" << endl;
          return "";
        }
      received_message = string(buf, 0, bytes_received);
      last_message_received = received_message;
      return received_message;
    }
    else if (receiving_status == 0){
      cout << "Timeout reached in select()" << endl;
      return "";
    }
    else{
      cout << "Something wrong with select()" << endl;
      return "";
    }
  }



  bool send_message(string message){
    int sendRes = send(sock, message.c_str(), message.size() + 1, 0);
        if (sendRes == -1){
            cout << "Could not send message to Otter" << endl;
            return false;
        }
    return true;
  }



  bool drift(){
    cout << "Otter entering drift mode" << endl;
    string message_to_send = "$PMARABT\r\n";

    return send_message(message_to_send);
  }



  bool set_autopilot_mode(float cross_track_error_magnitude, string direction_to_steer, string cross_track_units, int bearing_from_origin_to_destination){
    return true;
  }



  bool set_manual_control_mode(float force_x = 0, float force_y = 0, float torque_z = 0){
    cout << "Otter entering manual control mode with X force: " << force_x << ", Y force: " << force_y << ", Z torque: " << torque_z << endl;
    string x_force = to_string(force_x).substr(0, 4);
    string y_force = to_string(force_y).substr(0, 4);
    string z_torque = to_string(torque_z).substr(0, 4);
    string message_to_send = "$PMARMAN," + x_force + "," + y_force + "," + z_torque + '*';

    message_to_send += checksum(message_to_send.substr(1, message_to_send.size()));
    message_to_send += "\r\n";

    return send_message(message_to_send);
  }



  bool set_course_mode(int angle, float speed){
    cout << "Otter entering course mode with angle: " << angle << ", speed: " << speed << endl;
    string message_to_send = "$PMARCRS," + to_string(angle) + "," + to_string(speed).substr(0, 4) + "*";

    message_to_send += checksum(message_to_send.substr(1, message_to_send.size()));
    message_to_send += "\r\n";

    return send_message(message_to_send);
  }



  bool set_leg_mode(float lat0, float lon0, float lat1, float lon1, float speed){
    cout << "Otter entering leg mode with lat0: " + to_string(lat0) + ", lon0: " + to_string(lon0) +
    ", lat1: " + to_string(lat1) + ", lon1: " + to_string(lon1) + ", speed: " + to_string(speed).substr(0, 4) << endl;

    lat0 *= 100;
    lon0 *= 100;
    lat1 *= 100;
    lon1 *= 100;

    string message_to_send = "$PMARLEG,";
    if (lat0 < 0){message_to_send += to_string(lat0).substr(0, 9);}
    else{message_to_send += to_string(lat0).substr(0, 8);}

    message_to_send += ",";

    if (lon0 < 0){message_to_send += to_string(lon0).substr(0, 10);}
    else{message_to_send += to_string(lon0).substr(0, 9);}

    message_to_send += ",";

    if (lat1 < 0){message_to_send += to_string(lat1).substr(0, 9);}
    else{message_to_send += to_string(lat1).substr(0, 8);}

    message_to_send += ",";

    if (lon1 < 0){message_to_send += to_string(lon1).substr(0, 10);}
    else{message_to_send += to_string(lon1).substr(0, 9);}

    message_to_send += ",";

    message_to_send += to_string(speed).substr(0, 4) + "*";

    message_to_send += checksum(message_to_send.substr(1, message_to_send.size()));
    message_to_send += "\r\n";

    return send_message(message_to_send);
  }



  bool set_station_mode(float latitude, float longitude, float speed){
    cout << "Otter entering station mode with latitude: " + to_string(latitude) +
    ", longitude: " + to_string(longitude) + ", speed: " + to_string(speed).substr(0, 4) << endl;

    latitude *= 100;
    longitude *= 100;

    string message_to_send = "$PMARSTA,";
    if (latitude < 0){message_to_send += to_string(latitude).substr(0, 9);}
    else{message_to_send += to_string(latitude).substr(0, 8);}

    message_to_send += ",";

    if (longitude < 0){message_to_send += to_string(longitude).substr(0, 10);}
    else{message_to_send += to_string(longitude).substr(0, 9);}

    message_to_send += ",";

    message_to_send += to_string(speed).substr(0, 4) + "*";

    message_to_send += checksum(message_to_send.substr(1, message_to_send.size()));
    message_to_send += "\r\n";

    return send_message(message_to_send);
  }














}; // End of otter_usv class definition
