OscIn oin;
OscMsg msg;
9011 => oin.port;
oin.addAddress( "/StereoEncoder/azimuth" );
oin.addAddress( "/StereoEncoder/elevation" );
Step stepAZ => OnePole lpAZ  => blackhole;
Step stepEL => OnePole lpEL  => blackhole;
0.99 => lpAZ.pole; 
0.99 => lpEL.pole; 

"127.0.0.1" => string DEST_HOST;
9020        => int DEST_PORT;   
OscOut xmit;
xmit.dest(DEST_HOST, DEST_PORT);

while( true )
{

    oin => now;
    

    while (oin.recv(msg)) {
        if (msg.numArgs() > 0) {
            if (msg.address == "/StereoEncoder/azimuth") {
            msg.getFloat(0) => float az;
            
            az => stepAZ.next;
            }
            else if (msg.address == "/StereoEncoder/elevation")
            {
            msg.getFloat(0) => float el;
            
            el => stepEL.next; 
                }
            
           
            chout <= "az:" <= lpAZ.last()
                  <= "  el:" <= lpEL.last()
                  <= IO.newline();
            chout.flush();
            
            xmit.start("/StereoEncoder/azimuth");
            lpAZ.last() => xmit.add;
            xmit.send();

            xmit.start("/StereoEncoder/elevation");
            lpEL.last() => xmit.add;
            xmit.send();
            
        }
    }
}