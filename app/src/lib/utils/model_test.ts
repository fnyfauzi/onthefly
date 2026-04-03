import { nginxUrl, isDev } from "$lib/constants";
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
  SphereGeometry,
  TubeGeometry,
  Vector3,
} from "three";
import { CSS2DObject, PDBLoader, type PDB } from "three/examples/jsm/Addons.js";

///
async function loadModel(
  files: string[],
  document?: Document,
  container?: Element | HTMLElement
): Promise<Object3D[]> {
  const loader = new PDBLoader();
  let pdbs: PDB[];
  if (isDev) {
    // pdbs = await Promise.all(files.map((e) => loader.loadAsync(`pdbs/${e}`)));
    pdbs = await Promise.all(files.map((e) => loader.loadAsync(`/test/${e}`)));
    // pdbs = await Promise.all(files.map((e) => loader.loadAsync(`/static/test/${e}`)));
  } else {
    pdbs = await Promise.all(
      // files.map((e) => loader.loadAsync(`${nginxUrl}/viewer/pdbs/${e}`))
      files.map((e) => loader.loadAsync(`${nginxUrl}/test/${e}`))
    );
  }
  const models: Object3D[] = [];
  pdbs.forEach((pdb) => {
    models.push(extractModel(pdb, document, container));
  });
  return models;
}

///
async function loadSingleWithText(
  file: string,
  document: Document,
  container: Element | HTMLElement
) {
  // const url: string = isDev ? `pdbs/${file}` : `${nginxUrl}/viewer/pdbs/${file}`;
  const url: string = isDev ? `/test/${file}` : `${nginxUrl}/test/${file}`;
  const pdb: PDB = await new PDBLoader().loadAsync(url);
  const model = extractModel(pdb, document, container);
  return model;
}

///
function extractModel(
  pdb: PDB,
  document?: Document,
  container?: Element | HTMLElement
): Object3D {
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
    // mesh.position.multiplyScalar(2);
    // mesh.scale.multiplyScalar(2);
    object3D.add(mesh);

    // Draw CSS Text
    if (document) {
      const atom = json.atoms[i];

      const el = document.getElementsByClassName("label-css2d");
      if (el.length) {
        el[0].remove(); // OK
        // container?.removeChild(el[0]) // OK
      }
      const div = document.createElement("div");
      div.className = "label-css2d";
      div.style.color =
        "rgb(" + atom[3][0] + "," + atom[3][1] + "," + atom[3][2] + ")";
      div.textContent = atom[4];
      container!.appendChild(div);

      const label = new CSS2DObject(div);
      label.position.copy(mesh.position);
      object3D.add(label);
    }
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

export { loadModel, loadSingleWithText };
