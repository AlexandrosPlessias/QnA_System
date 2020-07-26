import platform
import subprocess


def start_server():
    """ Starting the Server.

    Open cmd and run java command:
    java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000 -annotators pos -annotators ner
    For start StanfordCoreNLPServer at port localhost:9000 with java max heap size = 4 GB.

    :return:
    """

    # Check is system is Windows.
    if str(platform.system()) == 'Windows':
        p = subprocess.Popen('Start Stanford server.bat', creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        print('Only Windows supported')
        print('Contact in e-mail: alexpl1992@gmail.com')
        exit(0)


def stop_server():
    """ Stopping the Server.

    The server can be stopped programmatically by making a call to the /shutdown endpoint with an appropriate shutdown key.
    This key is saved to the file corenlp.shutdown in the directory specified by System.getProperty("java.io.tmpdir"); when the server starts.
    Typically this will be /tmp/corenlp.shutdown, though it can vary, especially on macOS. An example command to shut down the server would be:
    wget "localhost:9000/shutdown?key=`cat /tmp/corenlp.shutdown`" -O -
    If you start the server with -server_id SERVER_NAME it will store the shutdown key in a file called corenlp.shutdown.SERVER_NAME
    :return:
    """

    p = subprocess.Popen('Stop Stanford server.bat', creationflags=subprocess.CREATE_NEW_CONSOLE)
