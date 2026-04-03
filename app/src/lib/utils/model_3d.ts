import { nginxUrl } from "$lib/constants";
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
  apiPath: string,
  files: string[],
  document?: Document,
  container?: Element | HTMLElement
): Promise<Object3D[]> {
  // ): Promise<[Object3D[], number[][]]> {
  const loader = new PDBLoader();
  // loader.crossOrigin = "anonymous";
  // loader.setCrossOrigin("anonymous")
  // let pdbs: PDB[] = [];
  let pdbs: PDB[];
  pdbs = await Promise.all(files.map((e) => loader.loadAsync(`${nginxUrl}${apiPath}/${e}`)));
  // for (let i=0; i<files.length; i++) {
  //   pdbs.push(await loader.loadAsync(`${nginxUrl}${apiPath}/${files[i]}`));
  // }
  // }
  const models: Object3D[] = [];
  // const indicesH: number[][] = [];
  pdbs.forEach((pdb) => {
    models.push(extractModel(pdb, document, container));
    // const [_model, _indicesH] = extractModel(pdb, document, container);
    // models.push(_model);
    // indicesH.push(_indicesH);
  });
  return models;
  // return [models, indicesH];
}

///
// async function loadSingle(
//   name: string, // filename without extension
//   file: string,
//   module: string,
//   document?: Document,
//   container?: Element | HTMLElement
// ): Promise<Object3D> {
//   // ): Promise<[Object3D, number[]]> {
//   const url: string = isDev
//     ? `pdbs/${name}/${file}`
//     : `${nginxUrl}/protected/${module}/pdbs/${name}/${file}`;
//   const pdb: PDB = await new PDBLoader().loadAsync(url);
//   const model = extractModel(pdb, document, container);
//   return model;
//   // const [model, indicesH] = extractModel(pdb, document, container);
//   // return [model, indicesH];
// }

///
function extractModel(
  pdb: PDB,
  document?: Document,
  container?: Element | HTMLElement
): Object3D {
  // ): [Object3D, number[]] {
  let object3D = new Object3D();

  const geometryAtoms = pdb.geometryAtoms;
  const geometryBonds = pdb.geometryBonds;
  const json = pdb.json;

  // const indicesH: number[] = [];
  const posH: number[][] = [];

  // create the atoms
  // let sphere = new SphereGeometry(0.2);
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

    // Get H (hydrogen) position (x,y,z)
    const atom = json.atoms[i];
    // const elName = atom[4]; // F or H or Br
    if (atom[4] === "H") {
      // indicesH.push(i);
      posH.push([pos.x, pos.y, pos.z]);
      mesh.name = "H";
    }

    mesh.position.copy(pos);
    // mesh.position.multiplyScalar(2);
    // mesh.scale.multiplyScalar(2);
    object3D.add(mesh);

    // Draw CSS Text
    if (document) {
      const atom = json.atoms[i];

      // IF Displaying the Element
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

    const atom = json.atoms[i];
    // console.log(atom);

    // PDF
    let path = new CatmullRomCurve3([start, end]);
    let tube = new TubeGeometry(path, 1, 0.04);
    // let mesh = new Mesh(tube, new MeshBasicMaterial({ color: 0xcccccc }));
    let mesh = new Mesh(tube, new MeshPhongMaterial({ color: "white" }));

    for (const i in posH) {
      const x = posH[i][0];
      const y = posH[i][1];
      const z = posH[i][2];

      if (start.x === x && start.y === y && start.z === z) {
        // mesh.name = "polar";
        mesh.name = "H-bound";
        break;
      } else if (end.x === x && end.y === y && end.z === z) {
        // mesh.name = "polar";
        mesh.name = "H-bound";
        break;
      }
    }

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
  // return [object3D, indicesH];
}

// export { loadModel, loadSingle };
export { loadModel };
