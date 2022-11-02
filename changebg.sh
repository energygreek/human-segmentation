#!/bin/bash

[ ! $# -eq 5 ] && echo "Usage: changebg.sh <sdp file> <new bg image> <orinal bg color in hex> <rtp output src> <rtp payload type>" && exit

SDP_PATH=$1
NEWBG_PATH=$2
REPLACE_COLOR_HEX=$3
RTP_TARGET=$4
RTP_PAYLOAD_TYPE=$5

./ffmpeg -nostdin -loglevel error -i "$NEWBG_PATH" -protocol_whitelist "udp,rtp,file"  -i "$SDP_PATH" \
  -filter_complex "[1:v]chromakey=$REPLACE_COLOR_HEX:similarity=0.1:blend=0.0[co];[0:v][co]overlay[out]" -map "[out]" \
  -an -c:v libx264 -preset ultrafast -f rtp -payload_type "$RTP_PAYLOAD_TYPE" "$RTP_TARGET"