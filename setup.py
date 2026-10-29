from setuptools import find_packages, setup

setup(
    name="armador-de-imagenes",
    version="0.1.0",
    description="Motor local para recortar y unir capturas sin remuestreo.",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.7,<3.9",
    install_requires=["Pillow==9.5.0", "numpy==1.21.6"],
)
