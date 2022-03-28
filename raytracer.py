from math import sqrt, pow, pi
from PIL import Image

class Vector( object ):
	def __init__(self,x,y,z):
		self.x = x
		self.y = y
		self.z = z

	def dot(self, b):  # vector dot product
		return self.x*b.x + self.y*b.y + self.z*b.z

	def cross(self, b):  # vector cross product
		return (self.y*b.z-self.z*b.y, self.z*b.x-self.x*b.z, self.x*b.y-self.y*b.x)

	def magnitude(self): # vector magnitude
		return sqrt(self.x**2+self.y**2+self.z**2)

	def normal(self): # compute a normalized (unit length) vector
		mag = self.magnitude()
		return Vector(self.x/mag,self.y/mag,self.z/mag)

	def __add__(self, b):  # add another vector (b) to a given vector (self)
		return Vector(self.x + b.x, self.y+b.y, self.z+b.z)

	def __sub__(self, b):  # subtract another vector (b) from a given vector (self)
		return Vector(self.x-b.x, self.y-b.y, self.z-b.z)

	def __mul__(self, b):  # scalar multiplication of a given vector
		assert type(b) == float or type(b) == int
		return Vector(self.x*b, self.y*b, self.z*b)

class Sphere( object ):
	def __init__(self, center, radius, color):
		self.c = center
		self.r = radius
		self.col = color

	def intersection(self, l):
		q = l.d.dot(l.o - self.c)**2 - (l.o - self.c).dot(l.o - self.c) + self.r**2
		if q < 0:
			return Intersection( Vector(0,0,0), -1, Vector(0,0,0), self)
		else:
			d = -l.d.dot(l.o - self.c)
			d1 = d - sqrt(q)
			d2 = d + sqrt(q)
			if 0 < d1 and ( d1 < d2 or d2 < 0):
				return Intersection(l.o+l.d*d1, d1, self.normal(l.o+l.d*d1), self)
			elif 0 < d2 and ( d2 < d1 or d1 < 0):
				return Intersection(l.o+l.d*d2, d2, self.normal(l.o+l.d*d2), self)
			else:
				return Intersection( Vector(0,0,0), -1, Vector(0,0,0), self)

	def normal(self, b):
		return (b - self.c).normal()

class Triangle(object):
        def __init__(self, p1, p2, p3, color):
                self.p1 = p1
                self.p2 = p2
                self.p3 = p3
                self.col = color
                
                self.u = p2 - p1
                self.v = p3 - p1
        
        def intersection(self, l):
                dv=l.d.cross(self.v)
                dvu = dv.dot(self.u)
                if dvu == 0:
                        return Intersection( Vector(0,0,0), -1, Vector(0,0,0), self)               

        def normal(self, b):
                return self.u.cross(self.v).normal()

class Plane( object ):
	def __init__(self, point, normal, color):
		self.n = normal
		self.p = point
		self.col = color

	def intersection(self, l):
		d = l.d.dot(self.n)
		if d == 0:
			return Intersection( Vector(0,0,0), -1, Vector(0,0,0), self)
		else:
			d = (self.p - l.o).dot(self.n) / d
			return Intersection(l.o+l.d*d, d, self.n, self)

class Ray( object ):
	def __init__(self, origin, direction):
		self.o = origin
		self.d = direction

class Intersection( object ):
	def __init__(self, point, distance, normal, obj):
		self.p = point
		self.d = distance
		self.n = normal
		self.obj = obj

class LightSource(object):        
        def __init__(self):
                self.setLightPosition(-10,0,0)
                self.setLightColor(255,255,255)
                
        def setLightPosition(self,x,y,z):
                self.position = Vector(x,y,z)
                
        def setLightColor(self,R,G,B):
                self.color = Vector(R,G,B)


class Raytracer:
        AMBIENT = 0.1
        GAMMA_CORRECTION = 1/2.2
        
        def __init__(self):
                self.setCanvas(500,500)
                self.setCameraPosition(0,0,10)
                self.light=LightSource()
                self.objects = []
                self.__scene()
                
        def setCanvas(self,width,height):
                self.width=width
                self.height=height
                
        def setCameraPosition(self,x,y,z):
                self.camera = Vector(x,y,z)

        def renderScene(self,Label,ImageBox):
                img=Image.new("RGB",(self.width,self.height))
                for x in range(self.width):
                        Label.Text="Rendering image: {2:3.1f}%".format(x,self.width-1,(float(x)*100/float(self.width-1)))
                        
                        for y in range(self.height):  
                                ray = Ray( self.camera, (Vector(x/50.0-5,y/50.0-5,0) - self.camera).normal())
                                col = self.__trace(ray,10)
                                img.putpixel((x,(self.height-1)-y),self.__gammaCorrection(col)) 
                ImageBox.clear()
                img.save("image.png","PNG")
                
        def __scene(self):
                self.objects.append(Sphere(Vector(-3,4,-10), 2.0, Vector(0,255,0)))   # center, radius, color
                self.objects.append(Sphere(Vector(0,-4,-10),  1.5, Vector(255,0,0)))
                self.objects.append(Sphere(Vector(0,0,-12), 3.5, Vector(0,0,255)))
                self.objects.append(Plane(Vector(0,0,-12), Vector(0,0,1), Vector(255,255,255)))  # normal, point, color
                #self.objects.append(Triangle(Vector(-2,0,-10), Vector(2,0,-10),Vector(0,-4,-10), Vector(255,0,255)))  # point, point , point, color

        def __testRay(self,ray, ignore=None):
                intersect = Intersection( Vector(0,0,0), -1, Vector(0,0,0), None)

                for obj in self.objects:
                        if obj is not ignore:
                                currentIntersect = obj.intersection(ray)
                                if currentIntersect.d > 0 and intersect.d < 0:
                                        intersect = currentIntersect
                                elif 0 < currentIntersect.d < intersect.d:
                                        intersect = currentIntersect
                                        
                return intersect

        def __trace(self,ray, maxRecur):               
                if maxRecur < 0:
                        return (0,0,0)
                intersect = self.__testRay(ray)
                if intersect.d == -1:
                        col = vector(self.AMBIENT,self.AMBIENT,self.AMBIENT)
                elif intersect.n.dot(self.light.position - intersect.p) < 0:
                        col = intersect.obj.col * self.AMBIENT
                else:
                        lightRay = Ray(intersect.p, (self.light.position-intersect.p).normal())
                        if self.__testRay(lightRay, intersect.obj).d == -1:
                                lightIntensity = 1000.0/(4*pi*(self.light.position-intersect.p).magnitude()**2)
                                col = intersect.obj.col * max(intersect.n.normal().dot((self.light.position - intersect.p).normal()*lightIntensity), self.AMBIENT)
                        else:
                                col = intersect.obj.col * self.AMBIENT
                return col

        def __gammaCorrection(self,color):
                col=[]
                try:
                        col.append(int(pow(color.x/float(self.light.color.x),self.GAMMA_CORRECTION)*self.light.color.x))
                except ZeroDivisionError:
                        col.append(int(pow(0,self.GAMMA_CORRECTION)*self.light.color.x))
                try:
                        col.append(int(pow(color.y/float(self.light.color.y),self.GAMMA_CORRECTION)*self.light.color.y))
                except ZeroDivisionError:
                        col.append(int(pow(0,self.GAMMA_CORRECTION)*self.light.color.y))
                try:
                        col.append(int(pow(color.z/float(self.light.color.z),self.GAMMA_CORRECTION)*self.light.color.z))
                except ZeroDivisionError:
                        col.append(int(pow(0,self.GAMMA_CORRECTION)*self.light.color.z))     
                return tuple(col)
