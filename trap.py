from numpy import pi, sqrt, exp

class Laser_Trap(object):
	def __init__(self,
				NA=0.99,
				wavelength=1550*10**(-9),
				power=0.5,
				radius=50*10**(-9)):
		self.NA = NA
		self.wavelength = wavelength
		self.w_0 = wavelength / (2*NA)
		self.z_r = (pi * self.w_0**2)/wavelength
		self.I_0 = self.intensity_at_focus(power)

		self.radius = radius
		self.N = self.mass()/ (60 * 1.660539040*10**(-27))
		self.n_index = 1.44

	def mass(self):
		volume = (4/3)*pi*self.radius**3 #m^3
		density = 2200 #m^3kg^-1
		amu =  1.660539040*10**(-27)#kg
		massofatom = 60 * amu #kg
		return volume*density

	def waist(self, z):
		return  self.w_0*sqrt(1. + (z/self.z_r)**2)

	def intensity(self, z, r):
		return self.I_0*((self.w_0)/self.waist(z)) *\
		 		exp((-2*r**2)/self.waist(z)**2)

	def intensity_at_focus(self, power):
		return (2*power)/(pi*self.w_0**2)

	def lorentz_lorenz(self):
		N = 3/(4*pi*self.radius**3)
		ratio = (self.n_index - 1)/(self.n_index + 2)
		return (3*ratio/(4*pi*N))#*(4*pi*permativity

	def trap_stiff(self, pressure):
		alpha = self.lorentz_lorenz()
		print alpha
		top = 4*pi**(3)*alpha*pressure*self.NA**(4)
		bottom = 3*10**(8)*8.854810**(-12)*self.wavelength**(4)
		return top/bottom

	def trap_freq(self, pressure):
		return sqrt(self.trap_stiff(pressure)/self.mass())/(2*pi)

	# def laser_trap(self):
		# import numpy as np
	# 	steps = 30
	# 	z = np.linspace(-1, 1, steps)*10**-5
	# 	r = np.linspace(-1, 1, steps)*self.w_0
	# 	X, Y = np.meshgrid(z,r)
	# 	Z = -self.intensity(X, Y)
	# 	ax.plot_surface(X*10**6, Y*10**6, Z, rstride=1, cstride=1,
	# 		cmap=matplotlib.cm.coolwarm, linewidth=0)
	# 	ax.set_xlabel('beam axis ($\mu m$)')
	# 	ax.set_ylabel('radial ($\mu m$)')
	# 	ax.set_zlabel('Potential')


# fig = plt.figure()
# ax = fig.gca(projection='3d')
# ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
# 	cmap=matplotlib.cm.coolwarm, linewidth=0)
# ax.set_xlabel('beam axis ($\mu m$)')
# ax.set_ylabel('radial ($\mu m$)')
# ax.set_zlabel('Potential')
# plt.show()
