'''
Generates gif file from images.
'''
import imageio.v3
import os

outputFileName = input("Enter output GIF name (omit .gif extension): ")
assert len(outputFileName) >= 1 and not outputFileName.endswith(".gif")
pathToImageFiles = input("Enter path to the directory containing images: ")
assert len(pathToImageFiles) >= 1 and os.path.exists(pathToImageFiles) and os.path.isdir(pathToImageFiles)
filenames = os.listdir(pathToImageFiles)
filenames.sort(key = lambda name: int(name[:name.find(".")].split('-')[-1]))
validImageExtensions = [".png", ".jpg", "jpeg"]
frames = []
for name in filenames:
    isImgValid=False
    for ext in validImageExtensions:
        if name.endswith(ext):
            isImgValid = True
            break
    if isImgValid:
        image = imageio.v3.imread(os.path.join(pathToImageFiles,name))
        frames.append(image)
        
imageio.mimsave("{}.gif".format(outputFileName), frames, duration = 0.01, loop=1)