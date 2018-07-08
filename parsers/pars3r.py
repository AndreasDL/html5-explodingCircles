from tinytag import TinyTag
import os

dname = ""
outputName = "music.csv"

with open(outputName, 'w') as f:
    f.write("filename;title;artist;album;albumartist;audio_offset;bitrate;disc;disc_total;duration;filesize;genre;samplerate;track;track_total;year;\n")
    for root, subFolders, files in os.walk(dname):
        for item in files:
            if item.endswith(".mp3") or item.endswith(".wma"):
                fname = str(os.path.join(root,item))
                try:
                    tag = TinyTag.get(fname)
                    f.write(item  + ";" + 
                        str(tag.title)  + ";" +
                        str(tag.artist) + ";" + 
                        str(tag.album)  + ";" +

                        str(tag.albumartist)  + ";" +
                        str(tag.audio_offset) + ";" +
                        str(tag.bitrate)      + ";" +
                        str(tag.disc)         + ";" +
                        str(tag.disc_total)   + ";" + 
                        str(tag.duration)     + ";" +
                        str(tag.filesize)     + ";" +
                        str(tag.genre)        + ";" +
                        str(tag.samplerate)   + ";" +
                        str(tag.track)        + ";" +
                        str(tag.track_total)  + ";" +
                        str(tag.year)         + ";" +
                        "\n"
                    )
                except:
                    print("\t", fname, " not parsed")
            else:
                fname = str(os.path.join(root,item))
                print(fname, "not parsed")
    f.close()