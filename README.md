# Quarantine Files System (QFS)

This is a basic implementation of the Google File System (GFS), built by the Spring 2020 CS4280.01 Distributed Systems class taught by Prof. Andrew Cencini using Python and the Requests library as the finals project for the course. The original GFS paper could be found [here.](https://static.googleusercontent.com/media/research.google.com/en//archive/gfs-sosp2003.pdf)

The current build supports the basic commands of creating a file and directory, appending bytes to the files and reading from them, and has been tested to work smoothly in a setup consisting of 1 Master, 1 Client and 3 Chunkservers running concurrently on AWS.

*Quang (Hx): The code definitely could be improved to look cleaner, have more functionalities and more testing could be done to ensure that it works on a larger scale as well as to ensure it is failure-tolerant/expectant, but for now, the basic functionalities are largely working, and that alone is a cause for celebration.*

## Usage / Client Interaction

The client is the entrypoint for interaction with the file system. The basic functionalities could be used as follows:

**Create**: Call the client with an HTTP GET request formatted as such to create an empty file and empty directory respectively.

```
http://{client_ip_addr}/create/file/<file_path>
http://{client_ip_addr}/create/dir/<file_path>/
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

## Chunkserver

The chunkservers are responsible for storing the data in chunks of configurable sizes (Default: 64mb, set to 16b for testing purposes), each file having configurable number of replicas (Default: 3). Usually, for every functions, the client would ask the Master to retrieve the chunkhandles for any specified file in the metaadata, and the chunkserver would then be contacted by the client to perform whatever tasks on the specified chunks.

### Chunkserver Endpoints

Note that all of Chunkserver Endpoints are HTTP GET/POST requests, called by sending a JSON with the corresponding parameters.

#### Master → Chunkserver endpoints

**create**: Create a new chunk with the corresponding chunk_handle given by the master.

```
chunk_handle: hex string. The chunk handle of the chunk.

Return: bool. True means operation succeeded while False means otherwise.
```

**lease-grant**: Grant a lease to a chunk, designating a chunk as the primary.

```
chunk_handle: hex string. The chunkhandle of the respective chunk.
timestamp: string. The timestamp of when the chunk last received a lease in ISO 8601 format at UTC.
replica: list. A list containing the locations of the replica of the primary chunk.

Return: int. The size of the chunk being given the lease.
```

**lease**: Checks if a chunk has a lease

```
chunk_handle hex. The chunkhandle of the respective chunk.

Return: bool. Whether the chunk has a lease.
```

**chunk-inventory**: Replies with a message in the form of a JSON file to the Master to report on the chunkserver's current status.

```
Return: JSON/Dict. Each message would contain information on a random subset of chunks on the chunkserver.
For each chunk, the information reported include:

chunk_handle: hex. The chunk handle of the chunk.
mutating: bool. Whether the chunk is being mutated.
lease: string. The timestamp of when the chunk last received a lease in ISO 8601 format at GMT/UTC.
size: int. The size of the chunk ignoring the first 16 bytes.
```

**collect-garbage**: Receives a list of chunks to be deleted from the Master, then proceeds to delete these chunks as well as their replicas.

```
deleted_chunks: json. A json file containing the chunkhandle of chunks to be deleted by the chunkserver.

Return: bool. True/False. True means all chunks in the deleted_chunks list are deleted.
False means one, some or all chunks in the deleted_chunks list could not be deleted,
be it due to the chunks being missing from the chunkserver or other reasons.
```

#### Client → Chunkserver Endpoints

**read**: Reads the data at the chunk with the given chunk handle over the given byte range.

```
chunk_handle: hex. The chunk handle of the chunk.
start_byte: int. The index of the location of the first byte to be read.
byte_range: int. The range starting from the first byte over which data is to be read.

Return: base64-encoded string. The data that was read. Note that if the byte_range is greater
than the remaining byte on the chunk then everything would be read. 
```

**append**: Appends the given bytes at the respective chunk_handle. Note that the chunkserver upon receiving the bytes will only put the data in a buffer cache. The data will not be written until the client sends an append-requestconfirmation. For this reason the data must be numbered with an index that the client is responsible for maintaining.

Note that the data should be sent not only to the primary chunk but to all the replicas as well.

Note that simultaneous appends may be written to the buffer cache in a different order per each chunk replica. This is acceptable as per:

"The client pushes the data to all the replicas. A client can do so in any order."  (Section 3.1, p. 6)

```
chunk_handle: hex. The chunk handle of the chunk
data_index: int. The index of the client's append() call.
For instance if a client wants to append 32mb of data it would break this up into two append() calls with
indexes 1 and 2 that way the buffer isn't overwritten. Reusing indexes will result in overwriting buffer data.
data: base64-encoded string. The data to be appended. The specification means that the maximum amount of data
that could be appended for any append message is 1/4th of the Chunk Size (Default: 16mb).

Return: int. An int denoting the status of the request.

0: The operation succeeded. Data is written to the buffer and ready for appending
1: The operation failed because bytes > MAX_APPEND_LIMIT.
2: The operation failed for other reasons.
```

**append_request**: Request to append the sent data. From the client end, it should only send this to the primary.

```
chunk_handle: hex. The chunk handle of the chunk
data_index: int. The index of the client's append() call

Return: int. An int denoting the status of the request.

0: The operation succeeded.
1: The operation failed because the requested chunk has no data in cache to append.
2: The operation failed because bytes > The amount of space left on the chunk.
3: The operation failed for other reasons.
```
