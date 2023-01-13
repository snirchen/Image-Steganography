import utils

EXAMPLE_IMAGE = [[(0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0)],
                 [(0, 0, 0), (255, 255, 120), (0, 0, 0), (0, 0, 0)],
                 [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]]

EXAMPLE_TEXT = 'Hii'


def main():
    arr = utils.png_file_to_rgb_np_array_converter(r"test.png")
    # utils.np_array_to_png_file_converter(np_array=np.array(EXAMPLE_IMAGE), path_to_save_png_file=r'test.png')


if __name__ == '__main__':
    main()
