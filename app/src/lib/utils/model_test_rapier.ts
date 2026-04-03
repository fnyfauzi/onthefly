import { nginxUrl, isDev } from "$lib/constants";
import type { World } from "@dimforge/rapier3d";
import {
  BoxGeometry,
  CatmullRomCurve3,
  Color,
  IcosahedronGeometry,
  Mesh,
  MeshBasicMaterial,
  MeshPhongMaterial,
  MeshStandardMaterial,
  Object3D,
  Quaternion,
  SphereGeometry,
  TubeGeometry,
  Vector3,
} from "three";
import { CSS2DObject, PDBLoader, type PDB } from "three/examples/jsm/Addons.js";

///
async function loadModel(
  RAPIER: any,
  world: World,
  file: string,
) {
  // const url: string = isDev ? `pdbs/${file}` : `${nginxUrl}/viewer/pdbs/${file}`;
  const url: string = isDev ? `/test/${file}` : `${nginxUrl}/test/${file}`;
  const pdb: PDB = await new PDBLoader().loadAsync(url);
  const model = extractModel(pdb);

  // Rapier
  const size = 0.3 + Math.random() * 0.25;
  const range = 6;
  const density = size * 1.0;
  let x = Math.random() * range - range * 0.5;
  let y = Math.random() * range - range * 0.5 + 3;
  let z = Math.random() * range - range * 0.5;

  // Physics
  let rigidBodyDesc = RAPIER.RigidBodyDesc.dynamic()
    .setTranslation(x, y, z)
    // .setLinearDamping(1)
    // .setAngularDamping(1);
  let rigid = world.createRigidBody(rigidBodyDesc);
  // let points = geometry.attributes.position.array;
  // let colliderDesc = RAPIER.ColliderDesc.convexHull(points).setDensity(density);
  let colliderDesc = RAPIER.ColliderDesc.ball(size).setDensity(density);
  world.createCollider(colliderDesc, rigid);

  const sceneMiddle = new Vector3(0,0,0);

  function update() {
    rigid.resetForces(true);
    let { x, y, z } = rigid.translation();
    let pos = new Vector3(x, y, z);
    let dir = pos.clone().sub(sceneMiddle).normalize();
    let q = rigid.rotation();
    let rote = new Quaternion(q.x, q.y, q.z, q.w);
    model.rotation.setFromQuaternion(rote);
    rigid.addForce(dir.multiplyScalar(-0.5), true);
    model.position.set(x, y, z);
  }

  return { mesh: model, rigid, update };
}

///
function extractModel(pdb: PDB): Object3D {
  let object3D = new Object3D();

  const geometryAtoms = pdb.geometryAtoms;
  const geometryBonds = pdb.geometryBonds;
  const json = pdb.json;

  // create the atoms
  const sphere = new IcosahedronGeometry(0.4, 3);
  const pos = new Vector3();
  const color = new Color();
  for (let i = 0; i < geometryAtoms.attributes.position.count; i++) {
    pos.x = geometryAtoms.attributes.position.getX(i);
    pos.y = geometryAtoms.attributes.position.getY(i);
    pos.z = geometryAtoms.attributes.position.getZ(i);

    color.r = geometryAtoms.attributes.color.getX(i);
    color.g = geometryAtoms.attributes.color.getY(i);
    color.b = geometryAtoms.attributes.color.getZ(i);

    // let mesh = new Mesh(sphere, new MeshBasicMaterial({color: color}));
    let mesh = new Mesh(sphere, new MeshPhongMaterial({ color: color }));
    mesh.position.copy(pos);
    mesh.name = "atom";
    // mesh.position.multiplyScalar(2);
    // mesh.scale.multiplyScalar(2);
    object3D.add(mesh);
  }

  // create bindings
  const start = new Vector3(); // start position
  const end = new Vector3(); // end position
  for (let i = 0; i < geometryBonds.attributes.position.count; i += 2) {
    start.x = geometryBonds.attributes.position.getX(i);
    start.y = geometryBonds.attributes.position.getY(i);
    start.z = geometryBonds.attributes.position.getZ(i);

    end.x = geometryBonds.attributes.position.getX(i + 1);
    end.y = geometryBonds.attributes.position.getY(i + 1);
    end.z = geometryBonds.attributes.position.getZ(i + 1);

    // PDF
    let path = new CatmullRomCurve3([start, end]);
    let tube = new TubeGeometry(path, 1, 0.04);
    // let mesh = new Mesh(tube, new MeshBasicMaterial({ color: 0xcccccc }));
    let mesh = new Mesh(tube, new MeshPhongMaterial({ color: "white" }));
    mesh.name = "bound";
    object3D.add(mesh);

    // WEB
    // start.multiplyScalar(2);
    // end.multiplyScalar(2);
    // let mesh = new Mesh(box, new MeshBasicMaterial({ color: 'white' }));
    // mesh.position.copy(start);
    // mesh.position.lerp(end, 0.5);
    // mesh.scale.set(1, 1, start.distanceTo(end));
    // mesh.lookAt(end);
    // object3D.add(mesh);
  }

  // object3D.scale.set(0.5, 0.5, 0.5)
  return object3D;
}

export { loadModel };
