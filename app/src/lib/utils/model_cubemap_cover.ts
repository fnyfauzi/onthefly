import { nginxUrl, isDev } from "$lib/constants";
import {
  CatmullRomCurve3,
  Color,
  CubeTexture,
  DataTexture,
  Mesh,
  MeshPhongMaterial,
  MeshStandardMaterial,
  Object3D,
  Texture,
  SphereGeometry,
  TubeGeometry,
  Vector3,
  EquirectangularReflectionMapping,
  CubeReflectionMapping,
  IcosahedronGeometry,
} from "three";
import { CSS2DObject, PDBLoader, type PDB } from "three/examples/jsm/Addons.js";

///
async function loadModel(
  texture: DataTexture | CubeTexture | Texture,
  envMapType:
    | typeof EquirectangularReflectionMapping
    | typeof CubeReflectionMapping,
  isRealistic: boolean,
  document?: Document,
  container?: Element | HTMLElement
): Promise<Object3D> {
  const url: string = isDev ? `test/sample.pdb` : `${nginxUrl}/test/sample.pdb`;
  const pdb: PDB = await new PDBLoader().loadAsync(url);
  const model = extractModel(
    pdb,
    texture,
    envMapType,
    isRealistic,
    document,
    container
  );
  return model;
}


///
function extractModel(
  pdb: PDB,
  texture: DataTexture | CubeTexture | Texture,
  envMapType:
    | typeof EquirectangularReflectionMapping
    | typeof CubeReflectionMapping,
  isRealistic: boolean,
  document?: Document,
  container?: Element | HTMLElement
): Object3D {
  let object3D = new Object3D();

  const geometryAtoms = pdb.geometryAtoms;
  const geometryBonds = pdb.geometryBonds;
  const json = pdb.json;

  const posH: number[][] = [];

  // let sphere = new SphereGeometry(0.2);
  const sphere = new IcosahedronGeometry(0.4, 3);
  const pos = new Vector3();
  const color = new Color();

  // create the atoms
  for (let i = 0; i < geometryAtoms.attributes.position.count; i++) {
    // let startPosition = new Vector3();
    // startPosition.x = geometryAtoms.attributes.position.getX(i);
    // startPosition.y = geometryAtoms.attributes.position.getY(i);
    // startPosition.z = geometryAtoms.attributes.position.getZ(i);
    pos.x = geometryAtoms.attributes.position.getX(i);
    pos.y = geometryAtoms.attributes.position.getY(i);
    pos.z = geometryAtoms.attributes.position.getZ(i);

    // let color = new Color();
    color.r = geometryAtoms.attributes.color.getX(i);
    color.g = geometryAtoms.attributes.color.getY(i);
    color.b = geometryAtoms.attributes.color.getZ(i);

    // let material = new MeshPhongMaterial({ color: color }); // Original
    // let material = new MeshStandardMaterial({ color: 0xffea00, roughness: 0, metalness: 0.5 });
    let material = new MeshStandardMaterial({
      color: color,
      roughness: 0,
      metalness: 0.5,
    });
    if (!isRealistic) {
      material.envMap = texture;
      if (material.envMap?.isTexture) {
        material.envMap.mapping = envMapType;
      }
    }

    let mesh = new Mesh(sphere, material);
    // mesh.position.copy(startPosition);
    mesh.position.copy(pos);
    object3D.add(mesh);

    // Draw CSS Text
    if (document) {
      const atom = json.atoms[i];

      const el = document.getElementsByClassName("label-css2d-cubemap");
      if (el.length) {
        el[0].remove(); // OK
        // container?.removeChild(el[0]) // OK
      }
      const div = document.createElement("div");
      div.className = "label-css2d-cubemap";
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
    // let startPosition = new Vector3();
    // startPosition.x = geometryBonds.attributes.position.getX(i);
    // startPosition.y = geometryBonds.attributes.position.getY(i);
    // startPosition.z = geometryBonds.attributes.position.getZ(i);

    // let endPosition = new Vector3();
    // endPosition.x = geometryBonds.attributes.position.getX(i + 1);
    // endPosition.y = geometryBonds.attributes.position.getY(i + 1);
    // endPosition.z = geometryBonds.attributes.position.getZ(i + 1);

    start.x = geometryBonds.attributes.position.getX(i);
    start.y = geometryBonds.attributes.position.getY(i);
    start.z = geometryBonds.attributes.position.getZ(i);

    end.x = geometryBonds.attributes.position.getX(i + 1);
    end.y = geometryBonds.attributes.position.getY(i + 1);
    end.z = geometryBonds.attributes.position.getZ(i + 1);

    // use the start and end to create a curve, and use the curve to draw
    // a tube, which connects the atoms
    // let path = new CatmullRomCurve3([startPosition, endPosition]);
    let path = new CatmullRomCurve3([start, end]);
    let tube = new TubeGeometry(path, 1, 0.04);

    // let material = new MeshPhongMaterial({ color: 0xcccccc }); // Original
    let material = new MeshStandardMaterial({
      color: 0xffea00,
      roughness: 0,
      metalness: 0.5,
    });
    if (!isRealistic) {
      material.envMap = texture;
      if (material.envMap?.isTexture) {
        material.envMap.mapping = envMapType;
      }
    }

    let mesh = new Mesh(tube, material);
    object3D.add(mesh);
  }

  // object3D.scale.set(0.5, 0.5, 0.5)
  return object3D;
}

export { loadModel };

