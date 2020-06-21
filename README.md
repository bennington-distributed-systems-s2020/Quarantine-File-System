# Quarantine Files System (QFS)

This is a basic implementation of the Google File System (GFS), built using Python and the Requests library as the finals project for the Spring 2020 CS4280.01 Distributed Systems course taught by Prof. Andrew Cencini. The original GFS paper could be found [here.](https://static.googleusercontent.com/media/research.google.com/en//archive/gfs-sosp2003.pdf)

The current build supports the basic commands of creating a file and directory, appending bytes to the files and reading from them, and has been tested to work smoothly in a setup consisting of 1 Master, 1 Client and 3 Chunkservers running concurrently on AWS.

*Quang (Hx): The code definitely could be improved to look cleaner, have more functionalities and more testing could be done to ensure that it works on a larger scale as well as to ensure it is failure-tolerant/expectant, but for now, the basic functionalities are largely working, and that alone is a cause for celebration.*

## Usage / Client Interaction

The client is the entrypoint for interaction with the file system. The basic functionalities could be used as follows:

**Create**: Call the client with an HTTP GET request formatted as such to create an empty file and empty directory respectively.

```
http://{client_ip_addr}/create/file/<file_path>
http://{client_ip_addr}/create/dir/<file_path>
```

**Read**: Call the client with an HTTP GET request formatted as such to read from a file starting from *start_byte* over the range of *byte_range*

```
http://{client_ip_addr}/read/<file_path>/<start_byte>/<byte_range>
```

Note that start_byte has no functionality in this build, and is defaulted to start from 0. Implementing start byte calculation would not be hard, but seems superfluous for what essentially is a proof of concept.

**Append**: Call the client with an HTTP POST request along with a JSON formatted as such to append to a file

```
http://{client_ip_addr}/append
```
```
{
  "file_path": <path of file to append>
  "content": <content to append to file encoded using Base64 encoding>
}
```
