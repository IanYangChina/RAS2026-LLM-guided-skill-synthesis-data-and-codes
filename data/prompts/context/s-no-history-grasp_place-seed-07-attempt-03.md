## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.810, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.412) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_contact
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_goal
  weight: 0.4
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_contact
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.05
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  parameters:
    descend_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    descend_z_offset:
      type: scalar
      range:
      - -0.03
      - 0.0
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.05]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, -0.01]
  - parameter_bindings:
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.412
- **task_score** (E): 0.810
- **fitness_score**: 0.882  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1682 |
| descend_1 | 1.00 | 1.00 | 0.1036 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1433 |
| transport_1 | 0.00 | 1.00 | 0.1176 |
| descend_2 | 1.00 | 1.00 | 0.0933 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.505, 0.022, 0.034) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.022, 0.034)→(0.496, 0.021, 0.025) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 42.667 | 0.153 | 0.208 |
| lift_1 | lift | 1.00 / step_budget | (0.496, 0.021, 0.025)→(0.506, 0.021, 0.168) | (0.511, 0.022, 0.026)→(0.519, 0.022, 0.160) | 0.274→0.218 | 1.00 / 35.667 | 103.884 | 0.753 |
| transport_1 | approach | 0.00 / step_budget | (0.506, 0.021, 0.168)→(0.560, 0.118, 0.196) | (0.519, 0.022, 0.160)→(0.566, 0.119, 0.180) | 0.218→0.105 | 1.00 / 37.333 | 0.088 | 0.149 |
| descend_2 | descend | 1.00 / step_budget | (0.560, 0.118, 0.196)→(0.595, 0.196, 0.183) | (0.566, 0.119, 0.180)→(0.603, 0.199, 0.166) | 0.105→0.032 | 1.00 / 31.333 | 0.096 | 0.127 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.868
- phase_score: 0.768
- phase_breakdown.lift_object_score: 0.870
- phase_breakdown.place_goal_score: 0.640
- phase_breakdown.reach_object_score: 0.820
- phase_breakdown.grasp_contact_score: 0.869
- grasp_place_fitness: 0.911

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.911
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.868
- **Median Q (composite search score)**: 0.404
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.397


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24107,"average_solve_count":224.0,"average_success_count":224.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08057,"descend_1.speed":0.0268,"descend_2.descend_tolerance":0.02564,"descend_2.descend_z_offset":-0.00031,"descend_2.speed":0.0405,"lift_1.lift_height":0.17552,"transport_1.speed":0.14677},"optimized_scores":{"best_composite_score":0.44119,"best_fitness_score":0.91119,"best_task_score":0.86764},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.5093,0.03716,-0.00121],"force_p95":0.52324,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76486,"mean_force":0.09897,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49689,0.03807,0.02668]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16777.0,"contact_point_centroid":[0.50153,0.0573,0.10404],"force_p95":0.11214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33888,"mean_force":0.06397,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5007,0.03808,0.10192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20556.0,"contact_point_centroid":[0.50281,0.01945,0.10369],"force_p95":0.08727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31304,"mean_force":0.04977,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50073,0.03808,0.10214]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03959,-0.00213],"force_p95":0.16221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23091,"mean_force":0.13291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49951,0.0383,0.02612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21157.0,"contact_point_centroid":[0.55444,0.07223,0.18375],"force_p95":0.0896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19946,"mean_force":0.04694,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55165,0.09077,0.18248]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5233.0,"contact_point_centroid":[0.49967,0.01919,0.02651],"force_p95":0.06807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17896,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49825,0.0382,0.02478]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15479.0,"contact_point_centroid":[0.55133,0.11061,0.18496],"force_p95":0.10258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16387,"mean_force":0.06749,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55226,0.09146,0.18251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1901.0,"contact_point_centroid":[0.60414,0.127,0.16764],"force_p95":0.08902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16122,"mean_force":0.05209,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6002,0.14534,0.16746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1242.0,"contact_point_centroid":[0.59758,0.16395,0.17149],"force_p95":0.10132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15832,"mean_force":0.07351,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59982,0.14491,0.16822]},{"body_a":"world","body_b":"grasp_target","contact_count":2124.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5026,0.01775,0.2187]},{"body_a":"world","body_b":"grasp_target","contact_count":1468.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50569,0.03745,0.0857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4242.0,"contact_point_centroid":[0.4987,0.05755,0.02759],"force_p95":0.08274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0955,"mean_force":0.05198,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49826,0.0382,0.02479]}],"total_contact_groups":12},"final_pose_error":0.02556,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.618,0.15961,0.13105],"final_tcp_position":[0.61112,0.15762,0.14739],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":311.48915,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2124.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5075,0.03627,0.13781],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1468.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.50695,0.0389,0.03418],"tcp_start":[0.5075,0.03627,0.13781],"tcp_to_object_dist_end":0.00991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03866,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2132,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15957,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11275.0,"raw_peak_contact_force":0.23091,"tcp_end":[0.49823,0.0382,0.02475],"tcp_start":[0.50695,0.0389,0.03418],"tcp_to_object_dist_end":0.01423,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52105,0.03883,0.17553],"object_pos_start":[0.51243,0.03866,0.02554],"object_to_goal_dist_end":0.17364,"object_to_goal_dist_start":0.2132,"object_z_max":0.17534,"peak_contact_force":311.48915,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37479.0,"raw_peak_contact_force":0.76486,"subtask_id":"lift_object","tcp_end":[0.5079,0.03833,0.185],"tcp_start":[0.49823,0.0382,0.02475],"tcp_to_object_dist_end":0.01622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59499,0.13674,0.16854],"object_pos_start":[0.52105,0.03883,0.17553],"object_to_goal_dist_end":0.0538,"object_to_goal_dist_start":0.17364,"object_z_max":0.17566,"peak_contact_force":0.10065,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36636.0,"raw_peak_contact_force":0.19946,"tcp_end":[0.59177,0.13582,0.18462],"tcp_start":[0.5079,0.03833,0.185],"tcp_to_object_dist_end":0.01642,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":91.0,"n_steps_budget":1000.0,"object_pos_end":[0.618,0.15961,0.13105],"object_pos_start":[0.59499,0.13674,0.16854],"object_to_goal_dist_end":0.0213,"object_to_goal_dist_start":0.0538,"object_z_max":0.16854,"peak_contact_force":0.10079,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3143.0,"raw_peak_contact_force":0.16122,"subtask_id":"place_goal","tcp_end":[0.61112,0.15762,0.14739],"tcp_start":[0.59177,0.13582,0.18462],"tcp_to_object_dist_end":0.01785,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13546,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09996,"descend_1.speed":0.02387,"descend_2.descend_tolerance":0.01723,"descend_2.descend_z_offset":-0.00012,"descend_2.speed":0.03601,"lift_1.lift_height":0.1823,"transport_1.speed":0.12024},"optimized_scores":{"best_composite_score":0.40382,"best_fitness_score":0.87382,"best_task_score":0.79087},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.47994,0.04577,-0.00125],"force_p95":0.46932,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72279,"mean_force":0.08657,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46786,0.04678,0.02792]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.47161,0.066,0.10832],"force_p95":0.08429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32836,"mean_force":0.05888,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47143,0.04679,0.10562]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20714.0,"contact_point_centroid":[0.47369,0.0279,0.10566],"force_p95":0.08028,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30331,"mean_force":0.04982,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47131,0.04678,0.10418]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4828,0.04858,-0.00216],"force_p95":0.16903,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23976,"mean_force":0.13495,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47039,0.04705,0.02713]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4984.0,"contact_point_centroid":[0.47118,0.02796,0.02718],"force_p95":0.07894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19666,"mean_force":0.0432,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46918,0.04693,0.02591]},{"body_a":"world","body_b":"grasp_target","contact_count":2040.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48925,0.02169,0.21929]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20087.0,"contact_point_centroid":[0.50794,0.07924,0.20825],"force_p95":0.07707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13595,"mean_force":0.05003,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.504,0.0977,0.20787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15937.0,"contact_point_centroid":[0.50187,0.11547,0.20963],"force_p95":0.09004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12677,"mean_force":0.06141,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50324,0.09636,0.20722]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47739,0.04593,0.08632]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4182.0,"contact_point_centroid":[0.54652,0.19761,0.2224],"force_p95":0.09351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11027,"mean_force":0.07234,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54961,0.17878,0.21948]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4252.0,"contact_point_centroid":[0.46919,0.06628,0.02842],"force_p95":0.08586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10093,"mean_force":0.05207,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46918,0.04694,0.02592]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6092.0,"contact_point_centroid":[0.55606,0.16128,0.21868],"force_p95":0.07777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09894,"mean_force":0.05321,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54968,0.1789,0.21945]}],"total_contact_groups":12},"final_pose_error":0.01702,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57945,0.22069,0.19634],"final_tcp_position":[0.57202,0.2166,0.21383],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.72279,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2040.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48017,0.04444,0.13852],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.47759,0.04775,0.03443],"tcp_start":[0.48017,0.04444,0.13852],"tcp_to_object_dist_end":0.00989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04747,0.02545],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29117,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16533,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11036.0,"raw_peak_contact_force":0.23976,"tcp_end":[0.46915,0.04693,0.02588],"tcp_start":[0.47759,0.04775,0.03443],"tcp_to_object_dist_end":0.01357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48934,0.04811,0.17744],"object_pos_start":[0.4827,0.04747,0.02545],"object_to_goal_dist_end":0.20987,"object_to_goal_dist_start":0.29117,"object_z_max":0.17725,"peak_contact_force":0.08236,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37856.0,"raw_peak_contact_force":0.72279,"subtask_id":"lift_object","tcp_end":[0.47795,0.04706,0.18726],"tcp_start":[0.46915,0.04693,0.02588],"tcp_to_object_dist_end":0.01507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5354,0.14355,0.21309],"object_pos_start":[0.48934,0.04811,0.17744],"object_to_goal_dist_end":0.09869,"object_to_goal_dist_start":0.20987,"object_z_max":0.21307,"peak_contact_force":0.08906,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36024.0,"raw_peak_contact_force":0.13595,"tcp_end":[0.52899,0.14124,0.22942],"tcp_start":[0.47795,0.04706,0.18726],"tcp_to_object_dist_end":0.01769,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.57945,0.22069,0.19634],"object_pos_start":[0.5354,0.14355,0.21309],"object_to_goal_dist_end":0.03519,"object_to_goal_dist_start":0.09869,"object_z_max":0.21309,"peak_contact_force":0.09258,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10274.0,"raw_peak_contact_force":0.11027,"subtask_id":"place_goal","tcp_end":[0.57202,0.2166,0.21383],"tcp_start":[0.52899,0.14124,0.22942],"tcp_to_object_dist_end":0.01943,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04962,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09219,"descend_1.speed":0.04054,"descend_2.descend_tolerance":0.02024,"descend_2.descend_z_offset":-0.00056,"descend_2.speed":0.01017,"lift_1.lift_height":0.11774,"transport_1.speed":0.12632},"optimized_scores":{"best_composite_score":0.39176,"best_fitness_score":0.86176,"best_task_score":0.77081},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.534,-0.02085,-0.00109],"force_p95":0.56673,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77016,"mean_force":0.10485,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52095,-0.0209,0.02549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11781.0,"contact_point_centroid":[0.52556,-0.04017,0.07876],"force_p95":0.08169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32949,"mean_force":0.0594,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52483,-0.02098,0.07602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14213.0,"contact_point_centroid":[0.5262,-0.00202,0.07672],"force_p95":0.07785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32547,"mean_force":0.05098,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52472,-0.02098,0.07502]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53701,-0.02133,-0.00203],"force_p95":0.13419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15293,"mean_force":0.12548,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52344,-0.02093,0.02524]},{"body_a":"world","body_b":"grasp_target","contact_count":2176.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51378,-0.00964,0.21805]},{"body_a":"world","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52907,-0.02029,0.08499]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16549.0,"contact_point_centroid":[0.54671,0.01164,0.15229],"force_p95":0.09068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11105,"mean_force":0.06032,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54437,0.03063,0.15121]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8044.0,"contact_point_centroid":[0.58259,0.12089,0.1755],"force_p95":0.08809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10875,"mean_force":0.05873,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57735,0.13922,0.17679]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5312.0,"contact_point_centroid":[0.5232,-0.00188,0.02608],"force_p95":0.06873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09691,"mean_force":0.0409,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52215,-0.02091,0.02379]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8466.0,"contact_point_centroid":[0.57562,0.1603,0.17759],"force_p95":0.07985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09605,"mean_force":0.05506,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5781,0.14145,0.17707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4158.0,"contact_point_centroid":[0.52316,-0.04021,0.02648],"force_p95":0.08022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09504,"mean_force":0.05201,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52216,-0.02091,0.02379]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18765.0,"contact_point_centroid":[0.54453,0.04867,0.15169],"force_p95":0.07842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09503,"mean_force":0.0534,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54409,0.02975,0.15078]}],"total_contact_groups":12},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61169,0.21687,0.16993],"final_tcp_position":[0.60217,0.21276,0.18643],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.77016,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2176.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53014,-0.01962,0.13695],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1392.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53109,-0.02103,0.03395],"tcp_start":[0.53014,-0.01962,0.13695],"tcp_to_object_dist_end":0.00991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53687,-0.02121,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31676,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13417,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11270.0,"raw_peak_contact_force":0.15293,"tcp_end":[0.52212,-0.02091,0.02376],"tcp_start":[0.53109,-0.02103,0.03395],"tcp_to_object_dist_end":0.0149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.54547,-0.02165,0.12647],"object_pos_start":[0.53687,-0.02121,0.02586],"object_to_goal_dist_end":0.27011,"object_to_goal_dist_start":0.31676,"object_z_max":0.12636,"peak_contact_force":0.08094,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26142.0,"raw_peak_contact_force":0.77016,"subtask_id":"lift_object","tcp_end":[0.53187,-0.02112,0.13098],"tcp_start":[0.52212,-0.02091,0.02376],"tcp_to_object_dist_end":0.01433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56826,0.07736,0.15954],"object_pos_start":[0.54547,-0.02165,0.12647],"object_to_goal_dist_end":0.16334,"object_to_goal_dist_start":0.27011,"object_z_max":0.1595,"peak_contact_force":0.07366,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35314.0,"raw_peak_contact_force":0.11105,"tcp_end":[0.55867,0.07577,0.17358],"tcp_start":[0.53187,-0.02112,0.13098],"tcp_to_object_dist_end":0.01708,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.61169,0.21687,0.16993],"object_pos_start":[0.56826,0.07736,0.15954],"object_to_goal_dist_end":0.03905,"object_to_goal_dist_start":0.16334,"object_z_max":0.16991,"peak_contact_force":0.09599,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16510.0,"raw_peak_contact_force":0.10875,"subtask_id":"place_goal","tcp_end":[0.60217,0.21276,0.18643],"tcp_start":[0.55867,0.07577,0.17358],"tcp_to_object_dist_end":0.01948,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```